"""Module for managing volume-related operations in the service layer.

This module provides functionality for handling volume operations such as
creating, retrieving, updating, deleting, attaching, and detaching volumes.
It serves as an intermediary between the API layer and the domain layer,
coordinating volume-related tasks and managing database interactions.

The module includes classes for representing volume statuses and a manager
class for handling volume operations. It also defines named tuples for
storing volume and storage information.

Classes:
    VolumeStatus: Enum representing the possible status values for a volume.
    VolumeServiceLayerManager: Manager class for handling volume-related
        operations in the service layer.

Named tuples:
    VolumeData: Stores information about a volume, including name, format,
        size, description, storage ID, user ID, and read-only status.
    StorageInfo: Stores information about a storage, including ID, name,
        type, status, available space, and mount point.

This module interacts with the domain layer via RPC calls and uses a
unit of work pattern for database operations. It also integrates with
an event store for logging significant events related to volume operations.
"""

from __future__ import annotations

import enum
import uuid
from typing import Dict, List, Optional, cast
from collections import namedtuple

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks, periodic_task
from openvair.modules.volume.config import (
    DEFAULT_VOLUME_FORMAT,
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.volume.domain.base import BaseVolume
from openvair.modules.volume.adapters.orm import Volume, VolumeAttachVM
from openvair.modules.volume.service_layer import exceptions, unit_of_work
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.volume.adapters.serializer import DataSerializer
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.libs.messaging.clients.rpc_clients.vm_rpc_client import (
    VMServiceLayerRPCClient,
)
from openvair.libs.messaging.clients.rpc_clients.storage_rpc_client import (
    StorageServiceLayerRPCClient,
)

LOG = get_logger(__name__)


VolumeData = namedtuple(
    'VolumeData',
    [
        'name',
        'format',
        'size',
        'description',
        'storage_id',
        'user_id',
        'read_only',
    ],
)


StorageInfo = namedtuple(
    'StorageInfo',
    ['id', 'name', 'storage_type', 'status', 'available_space', 'mount_point'],
)


class VolumeStatus(enum.Enum):
    """Enum representing the possible status values for a volume.

    This enum defines the various states a volume can be in throughout its
    lifecycle in the system. It helps in tracking and managing the current
    state of a volume during operations such as creation, deletion, and error
    handling.

    Attributes:
        new (int): Indicates that the volume has been newly created or
            registered in the system but not yet processed.
        creating (int): Represents that the volume is currently in the process
            of being created.
        available (int): Signifies that the volume has been successfully created
            and is ready for use.
        error (int): Indicates that an error occurred during volume processing
            or management.
        deleting (int): Represents that the volume is in the process of being
            deleted from the system.
        extending (int): Indicates that the volume is in the process of being
            extended to a larger size.

    The integer values associated with each status are used for ordering and
    can be helpful in database representations or API responses.
    """

    new = 1
    creating = 2
    available = 3
    error = 4
    deleting = 5
    extending = 6


class VolumeServiceLayerManager(BackgroundTasks):
    """Manager class for handling volume-related operations in the service layer

    This class serves as the main entry point for volume management operations,
    coordinating interactions between the API layer, domain layer, and database.
    It handles tasks such as volume creation, retrieval, deletion, extension,
    attachment, detachment, and status management.

    The class inherits from BackgroundTasks, allowing it to perform periodic
    or background operations related to volume management.

    Attributes:
        uow (SqlAlchemyUnitOfWork): Unit of work for managing database
            transactions.
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
            with the API of service layer.
        storage_service_client (StorageServiceLayerClient): Client for
            communicating with the storage service layer.
        event_store (EventCrud): Event store for logging volume-related events.
    """

    def __init__(self) -> None:
        """Initialize the VolumeServiceLayerManager.

        This constructor sets up the necessary components for the
        VolumeServiceLayerManager, including:
        - Initializing the parent BackgroundTasks class
        - Setting up the unit of work for database operations
        - Configuring RPC clients for communication with domain and service
            layers
        - Initializing the storage service client
        - Setting up the event store for logging events

        The initialization ensures that the manager is ready to handle
        volume-related operations and maintain proper communication channels
        with other parts of the system.
        """
        super(VolumeServiceLayerManager, self).__init__()
        self.uow = unit_of_work.SqlAlchemyUnitOfWork()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )
        self.storage_service_client = StorageServiceLayerRPCClient()
        self.vm_service_client = VMServiceLayerRPCClient()
        self.event_store = EventCrud('volumes')

    def get_volume(self, data: Dict) -> Dict:
        """Retrieve a specific volume from the database.

        This method fetches a volume from the database based on the provided
        volume ID and returns its serialized representation.

        Args:
            data (Dict): A dictionary containing the volume ID.

        Returns:
            Dict: A dictionary representing the serialized volume with its
                metadata.

        Raises:
            UnexpectedDataArguments: If the provided data is missing the volume
                ID.
        """
        LOG.info('Service layer start handling response on get volume.')
        volume_id = data.pop('volume_id', None)
        LOG.debug('Get volume id from request: %s.' % volume_id)
        if not volume_id:
            message = (
                f'Incorrect arguments were received '
                f'in the request get volume: {data}.'
            )
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        with self.uow:
            db_volume = self.uow.volumes.get(volume_id)
            web_volume = DataSerializer.to_web(db_volume)
            LOG.debug('Got volume from db: %s.' % web_volume)
        LOG.info('Service layer method get volume was successfully processed')
        return web_volume

    def get_all_volumes(self, data: Dict) -> List:
        """Retrieve all volumes from the database.

        This method fetches all volumes from the database, optionally filtered
        by storage ID and availability status, and returns their serialized
        representations.

        Args:
            data (Dict): A dictionary containing optional filter parameters
                such as storage_id and free_volumes.

        Returns:
            List: A list of dictionaries representing the serialized volumes.
        """
        LOG.info('Service layer start handling response on get volumes.')
        storage_id = data.pop('storage_id', None)
        free_volumes = data.pop('free_volumes', False)
        with self.uow:
            if storage_id:
                db_volumes = self.uow.volumes.get_all_by_storage(storage_id)
            else:
                db_volumes = self.uow.volumes.get_all()
            web_volumes = []
            for db_volume in db_volumes:
                if free_volumes and db_volume.attachments:
                    continue
                web_volumes.append(DataSerializer.to_web(db_volume))
        LOG.info('Service layer method get volumes was successfully processed')
        return web_volumes

    @staticmethod
    def _prepare_volume_data(volume_info: Dict) -> VolumeData:
        """Prepare volume data for creation.

        This method extracts and prepares the volume information necessary
        for creating a new volume in the system.

        Args:
            volume_info (Dict): A dictionary containing the information for
                the new volume.

        Returns:
            VolumeData: A named tuple containing the prepared volume
                information.

        Raises:
            UnexpectedDataArguments: If the provided data is invalid or
                incomplete.
        """
        LOG.info('Start preparing information for creating volume in db.')
        volume = VolumeData(
            name=volume_info.pop('name', ''),
            description=volume_info.pop('description', ''),
            format=volume_info.pop('format', DEFAULT_VOLUME_FORMAT),
            size=int(volume_info.pop('size', 0)),
            storage_id=volume_info.pop('storage_id', ''),
            user_id=volume_info.pop('user_id', ''),
            read_only=volume_info.pop('read_only', False),
        )
        LOG.debug('Volume Data for creating: %s.' % volume._asdict())
        if not (volume_info or volume.size or volume.storage_id):
            message = 'Comes unexpected data for creating volume.'
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        LOG.info('Volume data was successfully prepared.')
        return volume

    def _check_volume_exists_on_storage(
        self,
        volume_name: str,
        storage_id: str,
    ) -> None:
        """Check if a volume with the given name already exists on the storage.

        Args:
            volume_name (str): The name of the volume to check.
            storage_id (str): The ID of the storage to check.

        Raises:
            VolumeExistsOnStorageException: If a volume with the given name
                already exists on the specified storage.
        """
        db_volume = self.uow.volumes.get_by_name_and_storage(
            volume_name, storage_id
        )
        if db_volume:
            message = (
                f'Volume with current name {volume_name} ' f'exists on storage.'
            )
            LOG.error(message)
            raise exceptions.VolumeExistsOnStorageException(message)

    @staticmethod
    def _check_volume_status(
        volume_status: str,
        available_statuses: List,
    ) -> None:
        """Check if the volume status is in the list of available statuses.

        Args:
            volume_status (str): The current status of the volume.
            available_statuses (List): A list of allowed statuses.

        Raises:
            VolumeStatusException: If the volume status is not in the list of
                available statuses.
        """
        if volume_status not in available_statuses:
            message = (
                f'Volume status is {volume_status} but '
                f'must be in {available_statuses}.'
            )
            LOG.error(message)
            raise exceptions.VolumeStatusException(message)

    @staticmethod
    def _check_volume_has_not_attachment(volume: Volume) -> None:
        """Check if the volume has no attachments.

        Args:
            volume (Volume): The volume object to check.

        Raises:
            VolumeHasAttachmentError: If the volume has any attachments.
        """
        if volume.attachments:
            message = f'Volume {volume.id} has attachments.'
            LOG.error(message)
            raise exceptions.VolumeHasAttachmentError(message)

    def _get_storage_info(self, storage_id: str) -> StorageInfo:
        """Retrieve storage information from the storage service.

        This method uses the RPC client to get information about a specific
        storage device.

        Args:
            storage_id (str): The ID of the storage to retrieve information for.

        Returns:
            StorageInfo: An object containing the retrieved storage information.
        """
        try:
            storage_info = self.storage_service_client.get_storage(
                {'storage_id': str(storage_id)}
            )
        except (RpcCallException, RpcCallTimeoutException) as err:
            message = f'An error occurred when getting storages: {err!s}'
            LOG.error(message)
            return StorageInfo(
                id='',
                name='',
                storage_type='',
                status='',
                available_space=0,
                mount_point='',
            )

        storage_extra_specs = storage_info.get('storage_extra_specs', {})
        return StorageInfo(
            id=storage_info.get('id'),
            name=storage_info.get('name'),
            storage_type=storage_info.get('storage_type'),
            status=storage_info.get('status'),
            available_space=int(storage_info.get('available', 0)),
            mount_point=storage_extra_specs.get('mount_point', ''),
        )

    @staticmethod
    def _check_storage_on_availability(storage: StorageInfo) -> None:
        """Check if the storage is available.

        This method verifies whether the given storage is in an 'available'
        status. If the storage is not available, it logs an error message and
        raises a StorageUnavailableException.

        Args:
            storage (StorageInfo): An object containing information about the
                storage, including its status.

        Raises:
            StorageUnavailableException: If the storage status is not
                'available'.
        """
        if storage.status != 'available':
            message = (
                f'Storage {storage.name} status is '
                f'{storage.status} but must be available'
            )
            LOG.error(message)
            raise exceptions.StorageUnavailableException(message)

    @staticmethod
    def _check_available_space_on_storage(
        volume_size: int, storage: StorageInfo
    ) -> None:
        """Check if there enough available space on the storage for the volume.

        This method verifies whether the storage has sufficient available space
        to accommodate the specified volume size. If the available space is
        insufficient, it logs an error message and raises a
        ValidateArgumentsError.

        Args:
            volume_size (int): The size of the volume to be checked.
            storage (StorageInfo): An object containing information about the
                storage, including its available space.

        Raises:
            ValidateArgumentsError: If the available space on the storage is
                less than the volume size.
        """
        if volume_size >= storage.available_space:
            message = (
                'Not enough available space on the ' 'storage %s.' % storage.id
            )
            LOG.error(message)
            raise exceptions.ValidateArgumentsError(message)

    def create_volume(self, volume_info: Dict) -> Dict:
        """Create a new volume in the system.

        This method creates a new volume in the database and initiates the
        volume creation process in the domain layer.

        Args:
            volume_info (Dict): A dictionary containing the volume information.

        Returns:
            Dict: A dictionary representing the serialized newly created volume.

        Raises:
            UnexpectedDataArguments: If the provided data is invalid or
                incomplete.
        """
        LOG.info('Service layer start handling response on create volume.')
        user_info = volume_info.pop('user_info', {})
        volume_info.update({'user_id': user_info.get('id', '')})
        volume = self._prepare_volume_data(volume_info)
        with self.uow:
            self._check_volume_exists_on_storage(volume.name, volume.storage_id)
            db_volume = cast(Volume, DataSerializer.to_db(volume._asdict()))
            db_volume.status = VolumeStatus.new.name
            LOG.info('Start inserting volume into db with status new.')
            self.uow.volumes.add(db_volume)
            self.uow.commit()
            serialized_volume = DataSerializer.to_web(db_volume)
            LOG.debug(
                'Serialized volume ready for other steps: %s'
                % serialized_volume
            )
        LOG.info('Cast _create_volume for other steps.')
        serialized_volume.update({'user_info': user_info})
        self.service_layer_rpc.cast(
            self._create_volume.__name__, data_for_method=serialized_volume
        )
        self.event_store.add_event(
            str(serialized_volume.get('id')),
            user_info.get('id'),
            self.create_volume.__name__,
            'Volume successfully inserted into db.',
        )
        LOG.info(
            'Service layer method create_volume was' 'successfully processed'
        )
        return serialized_volume

    def _create_volume(self, volume_info: Dict) -> None:
        """The function handles the process of creating a volume in the system.

        This method validates the storage availability, checks space, and
        initiates the volume creation in the domain layer.

        Args:
            volume_info (Dict): A dictionary containing volume information.

        Raises:
            CreateVolumeDataException: If the volume ID is not received.
        """
        LOG.info('Service layer start handling response on _create_volume.')
        volume_info.pop('user_info', {})
        volume_id = volume_info.get('id', '')
        storage_id = volume_info.get('storage_id', '')
        if not volume_id:
            message = 'Volume id was not received.'
            LOG.error(message)
            raise exceptions.CreateVolumeDataException(message)
        storage_info = self._get_storage_info(storage_id)
        with self.uow:
            db_volume = self.uow.volumes.get(uuid.UUID(volume_id))
            try:
                self._check_volume_status(
                    db_volume.status, [VolumeStatus.new.name]
                )
                db_volume.status = VolumeStatus.creating.name
                db_volume.path = storage_info.mount_point
                db_volume.storage_type = storage_info.storage_type
                self.uow.commit()
                self._check_storage_on_availability(storage_info)
                self._check_available_space_on_storage(
                    int(db_volume.size), storage_info
                )

                domain_volume = DataSerializer.to_domain(db_volume)
                LOG.info(
                    'Serialized volume which will call to domain '
                    'for creating: %s.' % domain_volume
                )
                result = self.domain_rpc.call(
                    BaseVolume.create.__name__, data_for_manager=domain_volume
                )
                LOG.debug('Result of rpc call to domain: %s.' % result)
                db_volume.status = VolumeStatus.available.name
                LOG.debug(
                    'Volume status was updated on %s.'
                    % VolumeStatus.available.name
                )
                self.event_store.add_event(
                    str(db_volume.id),
                    str(db_volume.user_id),
                    self.create_volume.__name__,
                    'Volume successfully created in the system.',
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    f'An error occurred when calling the '
                    f'domain layer while creating volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                self.event_store.add_event(
                    str(db_volume.id),
                    str(db_volume.user_id),
                    self.create_volume.__name__,
                    message,
                )
                raise
            except (
                exceptions.VolumeStatusException,
                exceptions.ValidateArgumentsError,
                exceptions.StorageUnavailableException,
            ) as err:
                message = (
                    f'An error occurred while creating ' f'volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                self.event_store.add_event(
                    str(db_volume.id),
                    str(db_volume.user_id),
                    self.create_volume.__name__,
                    message,
                )
                raise
            finally:
                self.uow.commit()
        LOG.info(
            'Service layer method _create_volume was' 'successfully processed'
        )

    def _check_vm_power_state(self, vm_id: str) -> None:
        """Check if a VM is in the 'shut_off' power state.

        This method retrieves the power state of a VM from the VM service and
        verifies if it is 'shut_off'. If not, it raises an exception.

        Args:
            vm_id (str): The ID of the VM to check.

        Raises:
            VmPowerStateIsNotShutOffException: If the VM's power state is not
                'shut_off'.
        """
        try:
            vm = self.vm_service_client.get_vm({'vm_id': vm_id})
        except (RpcCallException, RpcCallTimeoutException) as err:
            LOG.error(f'An error occurred when getting VM: {err!s}')
            raise
        if vm.get('power_state', '') != 'shut_off':
            message = f"Vm {vm.get('name', '')} power state is not shut off."
            LOG.error(message)
            raise exceptions.VmPowerStateIsNotShutOffException(message)

    def extend_volume(self, data: Dict) -> Dict:
        """Extend the size of an existing volume.

        This method initiates the process of extending a volume's size and
        updates its status accordingly.

        Args:
            data (Dict): A dictionary containing the volume ID and new size.

        Returns:
            Dict: A dictionary representing the serialized updated volume.

        Raises:
            UnexpectedDataArguments: If the provided data is invalid or
                incomplete.
            ValidateArgumentsError: If the new size is not larger than the
                current size.
        """
        LOG.info('Service layer start handling response on extend volume.')
        user_info = data.pop('user_info', {})
        volume_id = data.get('volume_id')
        new_size = data.get('new_size')
        LOG.debug('Get volume id from request: %s.' % volume_id)
        if not (volume_id and new_size):
            message = (
                f'Incorrect arguments were received '
                f'in the request get volume: {data}.'
            )
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)

        with self.uow:
            db_volume = self.uow.volumes.get(volume_id)
            try:
                self._check_volume_status(
                    db_volume.status, [VolumeStatus.available.name]
                )

                self._check_extended_size(db_volume.size, new_size)

                db_volume.status = VolumeStatus.extending.name
                serialized_volume = DataSerializer.to_domain(db_volume)
                LOG.debug('Got volume from db: %s.' % serialized_volume)
            except (
                exceptions.ValidateArgumentsError,
                exceptions.VolumeStatusException,
            ) as err:
                message = (
                    f'An error occurred while validating data in '
                    f'extend volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message

                self.event_store.add_event(
                    volume_id,
                    str(db_volume.user_id),
                    self.extend_volume.__name__,
                    message,
                )
                raise
            finally:
                self.uow.commit()

        LOG.info('Cast _extend_volume for other steps.')

        self.service_layer_rpc.cast(
            self._extend_volume.__name__,
            data_for_method={
                'volume': serialized_volume,
                'new_size': int(new_size),
                'user_info': user_info,
            },
        )

        self.event_store.add_event(
            volume_id,
            str(db_volume.user_id),
            self.extend_volume.__name__,
            'Volume successfully marked as extending.',
        )
        return DataSerializer.to_web(db_volume)

    @staticmethod
    def _check_extended_size(old_size: int, new_size: int) -> None:
        if old_size >= new_size:
            message = (
                f'New size {new_size} bytes must be bigger than'
                f' current size {old_size} bytes.'
            )
            LOG.error(message)
            raise exceptions.ValidateArgumentsError(message)

    def _extend_volume(self, data: Dict) -> None:
        """Extend the size of a volume in the domain layer.

        This method calls the domain layer to handle the actual volume extension
        and updates the database accordingly.

        Args:
            data (Dict): A dictionary containing the volume information and
                new size.

        Raises:
            RpcCallException: If an error occurs during the RPC call to the
                domain layer.
            RpcCallTimeoutException: If the RPC call to the domain layer times
                out.
            ValidateArgumentsError: If the storage availability checks fail.
            VmPowerStateIsNotShutOffException: If a VM attached to the volume is
                not in the 'shut_off' state.
        """
        volume = data.get('volume', {})
        new_size = int(data.get('new_size', ''))
        data.pop('user_info', {})

        with self.uow:
            db_volume = self.uow.volumes.get(volume.get('id'))
            try:
                storage = self._get_storage_info(str(db_volume.storage_id))
                self._check_storage_on_availability(storage)
                for attachment in db_volume.attachments:
                    self._check_vm_power_state(str(attachment.vm_id))
                self._check_available_space_on_storage(
                    db_volume.size - new_size, storage
                )
                self.domain_rpc.call(
                    BaseVolume.extend.__name__,
                    data_for_manager=data.get('volume'),
                    data_for_method=data.get('new_size'),
                )
                db_volume.status = VolumeStatus.available.name
                db_volume.size = new_size
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    f'An error occurred when calling the '
                    f'domain layer while extending volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                self.event_store.add_event(
                    volume.get('id'),
                    str(db_volume.user_id),
                    self._extend_volume.__name__,
                    message,
                )
                raise
            except (
                exceptions.StorageUnavailableException,
                exceptions.ValidateArgumentsError,
            ) as err:
                message = (
                    f'An error occurred while accessing '
                    f'the storage: {err!s}.'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                self.event_store.add_event(
                    volume.get('id'),
                    str(db_volume.user_id),
                    self._extend_volume.__name__,
                    message,
                )
                raise
            except exceptions.VmPowerStateIsNotShutOffException as err:
                message = (
                    f'An error occurred while checking attachments:' f'{err!s}.'
                )
                db_volume.status = VolumeStatus.available.name
                db_volume.information = message
                self.event_store.add_event(
                    volume.get('id'),
                    str(db_volume.user_id),
                    self._extend_volume.__name__,
                    message,
                )
                raise
            finally:
                self.uow.commit()

        self.event_store.add_event(
            volume.get('id'),
            str(db_volume.user_id),
            self._extend_volume.__name__,
            'Volume successfully extended.',
        )

        LOG.info(
            'Service layer method extend_volume' 'was successfully processed'
        )

    def delete_volume(self, data: Dict) -> Dict:
        """Delete a volume from the system.

        This method initiates the process of deleting a volume and updates
        its status accordingly.

        Args:
            data (Dict): A dictionary containing the volume ID.

        Returns:
            Dict: A dictionary representing the serialized volume being deleted.

        Raises:
            VolumeStatusException: If the volume is not in a valid state for
                deletion.
            VolumeHasAttachmentError: If the volume is still attached to a VM.
        """
        LOG.info('Service layer start handling response on delete volume.')
        user_info = data.pop('user_info', {})
        volume_id = data.get('volume_id', '')
        with self.uow:
            db_volume = self.uow.volumes.get(volume_id)
            available_statuses = [
                VolumeStatus.available.name,
                VolumeStatus.error.name,
            ]
            try:
                self._check_volume_status(db_volume.status, available_statuses)
                self._check_volume_has_not_attachment(db_volume)

                db_volume.status = VolumeStatus.deleting.name
                self.uow.commit()
                domain_volume = DataSerializer.to_domain(db_volume)
                domain_volume.update({'user_info': user_info})
                self.service_layer_rpc.cast(
                    self._delete_volume.__name__, data_for_method=domain_volume
                )
                self.event_store.add_event(
                    volume_id,
                    str(db_volume.user_id),
                    self.delete_volume.__name__,
                    'Volume successfully marked as deleting.',
                )
            except (
                exceptions.VolumeStatusException,
                exceptions.VolumeHasAttachmentError,
            ) as err:
                message = (
                    f'An error occurred when deleting the ' f'volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                self.event_store.add_event(
                    volume_id,
                    str(db_volume.user_id),
                    self.delete_volume.__name__,
                    message,
                )
                raise
            finally:
                self.uow.commit()
        return DataSerializer.to_web(db_volume)

    def _delete_volume(self, volume_info: Dict) -> None:
        """Delete a volume from the system.

        This method handles the deletion of a volume from the system, ensuring
        that the volume is properly removed from the database and any associated
        storage is checked for availability.

        Args:
            volume_info (Dict): A dictionary containing information about the
                volume to be deleted. It should include the volume's ID and
                storage ID.

        Returns:
            None: This function does not return a value. It performs the
            deletion operation and logs the result.
        """
        volume_info.pop('user_info')
        with self.uow:
            db_volume = self.uow.volumes.get(volume_info.get('id', ''))
            try:
                if db_volume.storage_type:
                    self.domain_rpc.call(
                        BaseVolume.delete.__name__, data_for_manager=volume_info
                    )
                self.uow.session.delete(db_volume)
                self.event_store.add_event(
                    str(volume_info.get('id')),
                    str(db_volume.user_id),
                    self._delete_volume.__name__,
                    'Volume successfully deleted from the system.',
                )
                LOG.info(
                    'Service layer method delete_volume '
                    'was successfully processed'
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    f'An error occurred when calling the '
                    f'domain layer while deleting volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                self.event_store.add_event(
                    str(volume_info.get('id')),
                    str(db_volume.user_id),
                    self._delete_volume.__name__,
                    message,
                )
                raise
            finally:
                self.uow.commit()

    def edit_volume(self, data: Dict) -> Dict:
        """Edit the metadata of an existing volume.

        This method updates the name, read-only status, and description of a
        volume.

        Args:
            data (Dict): A dictionary containing the updated volume information.

        Returns:
            Dict: A dictionary representing the serialized updated volume.

        Raises:
            VolumeStatusException: If the volume is not in a valid state for
                editing.
        """
        LOG.info('Service layer start handling response on edit volume.')
        new_volume_name = data.get('name', '')
        new_read_only = data.get('read_only', False)
        new_volume_description = data.get('description', '')
        with self.uow:
            db_volume = self.uow.volumes.get(data.get('volume_id', ''))
            self._check_volume_status(
                db_volume.status, [VolumeStatus.available.name]
            )
            if new_volume_name and new_volume_name != db_volume.name:
                self._check_volume_exists_on_storage(
                    new_volume_name, str(db_volume.storage_id)
                )
            db_volume.name = new_volume_name
            db_volume.read_only = new_read_only
            db_volume.description = new_volume_description
            self.uow.commit()
        serialized_volume = DataSerializer.to_web(db_volume)
        LOG.info('Service layer method edit_volume was successfully processed')
        return serialized_volume

    def attach_volume(self, data: Dict) -> Dict:
        """Attach a volume to a virtual machine.

        This method creates an attachment between a volume and a VM and updates
        the volume's status accordingly.

        Args:
            data (Dict): A dictionary containing the volume ID and VM ID.

        Returns:
            Dict: A dictionary representing the result of the attachment
                operation.

        Raises:
            VolumeStatusException: If the volume is not in a valid state for
                attachment.
        """
        LOG.info('Starting attach volume to vm.')
        with self.uow:
            db_volume = self.uow.volumes.get(data.get('volume_id', ''))
            available_statuses = [VolumeStatus.available.name]
            try:
                self._check_volume_status(db_volume.status, available_statuses)
                attachment = cast(
                    VolumeAttachVM,
                    DataSerializer.to_db(data, VolumeAttachVM),
                )
                db_volume.attachments.append(attachment)
                serialized_volume = DataSerializer.to_domain(db_volume)
                result: Dict = self.domain_rpc.call(
                    BaseVolume.attach_volume_info.__name__,
                    data_for_manager=serialized_volume,
                )
                LOG.info('Volume was successfully attached.')
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    f'An error occurred when calling the '
                    f'domain layer while attaching volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                raise
            except exceptions.VolumeStatusException as err:
                message = (
                    f'An error occurred while attaching ' f'volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                raise
            else:
                return result
            finally:
                self.uow.commit()

    def detach_volume(self, data: Dict) -> Dict:
        """Detach a volume from a virtual machine.

        This method removes the attachment between a volume and a VM and updates
        the volume's status accordingly.

        Args:
            data (Dict): A dictionary containing the volume ID and VM ID.

        Returns:
            Dict: A dictionary representing the serialized updated volume.

        Raises:
            VolumeStatusException: If the volume is not in a valid state for
                detachment.
        """
        LOG.info('Starting detaching volume.')
        volume_id = data.get('volume_id', '')
        vm_id = data.get('vm_id', '')
        with self.uow:
            db_volume = self.uow.volumes.get(volume_id)
            available_statuses = [
                VolumeStatus.available.name,
                VolumeStatus.error.name,
            ]
            try:
                self._check_volume_status(db_volume.status, available_statuses)
                for attachment in db_volume.attachments:
                    if str(attachment.vm_id) == vm_id:
                        db_volume.attachments.remove(attachment)
                        self.uow.session.delete(attachment)
                LOG.info('Volume was successfully detached.')
            except exceptions.VolumeStatusException as err:
                message = (
                    f'An error occurred while detaching ' f'volume: {err!s}'
                )
                db_volume.status = VolumeStatus.error.name
                db_volume.information = message
                raise
            finally:
                self.uow.commit()
        return DataSerializer.to_web(db_volume)

    def _get_all_storages_info(self) -> List[StorageInfo]:
        """Retrieve information about all available storages.

        This method uses the storage service client to fetch details about
        all available storages in the system.

        Returns:
            List[StorageInfo]: A list of `StorageInfo` objects containing
                details about each storage.
        """
        prepared_storages: List = []
        try:
            storages = self.storage_service_client.get_all_storages()
        except (RpcCallException, RpcCallTimeoutException) as err:
            LOG.error(f'An error occurred when getting storages: {err!s}')
            return prepared_storages

        for storage in storages:
            storage_extra_specs = storage.get('storage_extra_specs', {})
            prepared_storages.append(
                StorageInfo(
                    id=storage.get('id'),
                    name=storage.get('name'),
                    storage_type=storage.get('storage_type'),
                    status=storage.get('status'),
                    available_space=int(storage.get('available', 0)),
                    mount_point=storage_extra_specs.get('mount_point', ''),
                )
            )
        return prepared_storages

    @periodic_task(interval=10)
    def monitoring(self) -> None:
        """Periodic task for monitoring the state of volumes in the system.

        This method is responsible for periodically monitoring the status of
        volumes in the system. It retrieves all volumes from the database,
        checks their status and the availability of their associated storage,
        and updates the volume information accordingly.

        The method performs the following steps:

        1. Retrieve all volumes from the database.
        2. Get information about all available storage devices.
        3. For each volume:
        - Retrieve the storage information for the volume.
        - Validate the volume status and storage availability.
        - Get updated volume information from the domain layer.
        - Update the volume information in a list for subsequent database
            update.
        - Handle any exceptions that occur during the process.
        4. Update the volume information in the database in bulk.

        This method is designed to run periodically using the `@periodic_task`
        decorator, with an interval of 10 seconds.
        """
        LOG.info('Start monitoring.')

        domain_volumes = self._get_domain_volumes()
        if not domain_volumes:
            LOG.info("Stop monitoring. Volumes don't exist.")
            return

        storages = self._get_storages_dict()
        updated_db_volumes = self._process_volumes(domain_volumes, storages)

        self._update_volumes_in_db(updated_db_volumes)
        LOG.info('Stop monitoring.')

    def _get_domain_volumes(self) -> List[Dict]:
        """Fetch all volumes as domain objects from the database.

        Returns:
            List[Dict]: A list of domain objects representing volumes.
        """
        with self.uow:
            return [
                DataSerializer.to_domain(vol)
                for vol in self.uow.volumes.get_all()
            ]

    def _get_storages_dict(self) -> Dict[str, StorageInfo]:
        """Get information about all available storages as a dictionary.

        Returns:
            Dict[str, StorageInfo]: A dictionary where the key is the storage ID
                                    and the value is the storage information.
        """
        return {
            storage.id: storage for storage in self._get_all_storages_info()
        }

    def _process_volumes(
        self, domain_volumes: List[Dict], storages: Dict[str, StorageInfo]
    ) -> List[Dict]:
        """Process each volume and prepare updated information.

        This method processes volumes and returns a list of updated information
        for the database.

        Args:
            domain_volumes (List[Dict]): A list of domain objects representing
                volumes.
            storages (Dict[str, StorageInfo]): A dictionary with storage
                information.

        Returns:
            List[Dict]: A list of updated volume data for the database.
        """
        updated_db_volumes = []
        for domain_volume in domain_volumes:
            try:
                updated_volume = self._process_single_volume(
                    domain_volume, storages
                )
                if updated_volume:
                    updated_db_volumes.append(updated_volume)
            except (
                exceptions.VolumeHasNotStorage,
                exceptions.StorageUnavailableException,
                exceptions.VolumeStatusException,
                RpcCallException,
                RpcCallTimeoutException,
            ) as error:
                LOG.error(
                    f"Error processing volume {domain_volume.get('id')}: "
                    f"{error!s}"
                )
        return updated_db_volumes

    def _process_single_volume(
        self, domain_volume: Dict, storages: Dict[str, StorageInfo]
    ) -> Optional[Dict]:
        """Process a single volume and get updated information.

        Checks if the storage for the volume exists, validates the volume
        status, and calls the domain method to get updated volume data.

        Args:
            domain_volume (Dict): Volume data.
            storages (Dict[str, StorageInfo]): A dictionary with storage
                information.

        Returns:
            Optional[Dict]: Updated volume information if available,
                otherwise None.
        """
        volume_storage = storages.get(domain_volume.get('storage_id', ''))
        if not volume_storage:
            raise exceptions.VolumeHasNotStorage(
                domain_volume.get('id', 'None')
            )

        self._check_storage_on_availability(volume_storage)
        self._check_volume_status(
            domain_volume.get('status', ''), self._get_monitoring_statuses()
        )

        result = self.domain_rpc.call(
            BaseVolume.attach_volume_info.__name__,
            data_for_manager=domain_volume,
        )

        return {
            'id': domain_volume.get('id'),
            'size': result.get('size', domain_volume['size']),
            'used': result.get('used', 0),
            'status': VolumeStatus.available.name,
            'information': '',
        }

    def _get_monitoring_statuses(self) -> List[str]:
        """Get the list of statuses for monitoring.

        Returns:
            List[str]: A list of volume statuses to be monitored.
        """
        return [
            VolumeStatus.available.name,
            VolumeStatus.error.name,
            VolumeStatus.creating.name,
            VolumeStatus.deleting.name,
            VolumeStatus.extending.name,
        ]

    def _update_volumes_in_db(self, updated_db_volumes: List[Dict]) -> None:
        """Update volume information in the database.

        This method performs a bulk update of volume information in the
        database.

        Args:
            updated_db_volumes (List[Dict]): A list of updated volume data.
        """
        with self.uow:
            self.uow.volumes.bulk_update(updated_db_volumes)
            self.uow.commit()
