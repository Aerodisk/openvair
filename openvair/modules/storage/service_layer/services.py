"""Module for managing storage-related operations in the service layer.

This module provides functionality for handling storage operations such as
creating, retrieving, updating, and deleting storages. It serves as an
intermediary between the API layer and the domain layer, coordinating
storage-related tasks and managing database interactions.

The module includes classes for representing storage statuses and a manager
class for handling storage operations in the service layer. It also defines
named tuples for storing storage information.

Classes:
    StorageStatus: Enum representing the possible status values for a storage.
    StorageServiceLayerManager: Manager class for handling storage-related
        operations in the service layer.

This module interacts with the domain layer via RPC calls and uses a
unit of work pattern for database operations. It also integrates with
an event store for logging significant events related to storage operations.
"""

from __future__ import annotations

import enum
import uuid
from typing import Dict, List, cast

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks, periodic_task
from openvair.libs.context_managers import synchronized_session
from openvair.modules.storage.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.storage.domain import base
from openvair.modules.storage.adapters import orm
from openvair.libs.messaging.exceptions import (
    RpcException,
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.storage.libs.utils import (
    is_system_disk,
    get_system_disks,
    is_system_partition,
    get_local_partitions,
)
from openvair.modules.storage.service_layer import exceptions, unit_of_work
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.storage.adapters.serializer import DataSerializer
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.libs.messaging.clients.rpc_clients.image_rpc_client import (
    ImageServiceLayerRPCClient,
)
from openvair.libs.messaging.clients.rpc_clients.volume_rpc_client import (
    VolumeServiceLayerRPCClient,
)
from openvair.libs.messaging.clients.rpc_clients.template_prc_client import (
    TemplateServiceLayerRPCClient,
)

LOG = get_logger(__name__)


class StorageStatus(enum.Enum):
    """Enum representing the possible status values for a storage.

    This enum defines the various states a storage can be in throughout its
    lifecycle in the system. It helps in tracking and managing the current
    state of a storage during operations such as creation, deletion, and error
    handling.

    Attributes:
        new (int): Indicates that the storage has been newly created or
            registered in the system but not yet processed.
        creating (int): Represents that the storage is currently in the process
            of being created in the system.
        available (int): Signifies that the storage has been successfully
            created and is ready for use.
        error (int): Indicates that an error occurred during storage processing
            or management.
        deleting (int): Represents that the storage is in the process of being
            deleted from the system.
        disconnected (int): Indicates that the storage is currently disconnected
            or unavailable.

    The integer values associated with each status are used for ordering and
    can be helpful in database representations or API responses.
    """

    new = 1
    creating = 2
    available = 3
    error = 4
    deleting = 5
    disconnected = 6


class StorageServiceLayerManager(BackgroundTasks):
    """Manager for handling storage-related operations in the service layer.

    This class serves as the main entry point for storage management operations,
    coordinating interactions between the API layer, domain layer, and database.
    It handles tasks such as storage creation, retrieval, deletion, and status
    management.
    The class inherits from BackgroundTasks, allowing it to perform periodic
    or background operations related to storage management.
    The class provides methods for various storage operations, including error
    handling and interaction with external services like volume and image
    management.

    Attributes:
        uow (SqlAlchemyUnitOfWork): Unit of work for managing database
            transactions.
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
            with the API of service layer.
        event_store (EventCrud): Event store for logging storage-related events.
    """

    def __init__(self) -> None:
        """Initialize the StorageServiceLayerManager.

        This constructor sets up the necessary components for the
        StorageServiceLayerManager, including:
        - Initializing the parent BackgroundTasks class
        - Setting up the unit of work for database operations
        - Configuring RPC clients for communication with domain and service
            layers
        - Initializing the event store for logging events

        The initialization ensures that the manager is ready to handle
        storage-related operations and maintain proper communication channels
        with other parts of the system.
        """
        super().__init__()
        self.uow = unit_of_work.SqlAlchemyUnitOfWork()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )
        self.volume_service_client = VolumeServiceLayerRPCClient()
        self.image_service_client = ImageServiceLayerRPCClient()
        self.template_service_client = TemplateServiceLayerRPCClient()
        self.event_store = EventCrud('storages')

    def get_storage(self, data: Dict) -> Dict:
        """Retrieve a specific storage from the database.

        The function gets a storage id from the request data, gets the storage
        from the database, serializes it to web format, and returns it.

        Args:
            data (Dict): A dictionary containing the storage ID.

        Returns:
            Dict: A dictionary representing the serialized storage with its
                metadata.

        Raises:
            StorageAttributeError: If the provided data is missing the storage
                ID.
        """
        LOG.info('Service layer start handling response on get storage.')
        storage_id = data['storage_id']
        LOG.debug('Get storage id from request: %s.' % storage_id)
        if not storage_id:
            message = (
                'Incorrect arguments were received '
                f'in the request get storage: {data}.'
            )
            LOG.error(message)
            raise exceptions.StorageAttributeError(message)
        with self.uow:
            db_storage = self.uow.storages.get(storage_id)
            web_storage = DataSerializer.to_web(db_storage)
            LOG.debug('Got storage from db: %s.' % web_storage)
        LOG.info('Service layer method get storage was successfully processed')
        return web_storage

    def get_all_storages(self) -> List[Dict]:
        """Retrieve all storages from the database.

        The function gets all storages from the database, serializes them
        to web format, and returns them as a list.

        Returns:
            List[Dict]: A list of dictionaries representing the serialized
                storages with their metadata.
        """
        LOG.info('Start getting storages from db.')
        with self.uow:
            web_storages = []
            db_storages = self.uow.storages.get_all()
            for db_storage in db_storages:
                web_storage = DataSerializer.to_web(db_storage)
                web_storages.append(web_storage)
        return web_storages

    def _check_storage_exists_with_current_name(
        self, storage_name: str
    ) -> None:
        """Checks if a storage with the given name already exists.

        The function checks if a storage with the given name already exists
        in the database. If it does, the function raises an exception.

        Args:
            storage_name (str): The name of the storage to check.

        Raises:
            ValueError: If the provided storage name is empty.
            StorageExistsError: If a storage with the given name already exists.

        """
        if not storage_name:
            msg = 'Storage name should not be empty.'
            raise ValueError(msg)
        with self.uow:
            storage = self.uow.storages.get_storage_by_name(storage_name)
            if storage:
                message = f'Storage with current name {storage_name} exists.'
                LOG.error(message)
                raise exceptions.StorageExistsError(message)

    def _check_spec_exists_for_nfs_storage(self, specs: Dict) -> None:
        """Check if a storage with the given spec for NFS already exists.

        Args:
            specs (Dict): A dictionary containing the specifications for the NFS
                storage.

        Raises:
            StorageExistsError: If a storage with the given specifications
                already exists.
        """
        LOG.info('Checking if storage with the given specs exists...')
        for key, value in specs.items():
            db_spec = self.uow.storages.get_spec_by_key_value(key, value)
            if db_spec:
                self._check_storage_specs(db_spec, specs)

    def _check_storage_specs(
        self,
        db_spec: orm.StorageExtraSpecs,
        specs: Dict,
    ) -> None:
        """Check if the database spec matches the given specs.

        Args:
            db_spec: The database specification object.
            specs (Dict): A dictionary containing the specifications for the NFS
                storage.

        Raises:
            StorageExistsError: If a storage with the given specifications
                already exists.
        """
        if not db_spec:
            return
        for storage_spec in db_spec.storage.extra_specs:
            if self._spec_matches(storage_spec, specs):
                message = (
                    f'Storage {db_spec.storage.id} exists '
                    f'with current specs {specs}.'
                )
                LOG.error(message)
                raise exceptions.StorageExistsError(message)

    def _spec_matches(
        self,
        storage_spec: orm.StorageExtraSpecs,
        specs: Dict,
    ) -> bool:
        """Check if a storage spec matches the given specs.

        Args:
            storage_spec: The storage specification to check.
            specs (Dict): A dictionary containing the specifications for the
                NFS storage.

        Returns:
            bool: True if the storage spec matches, False otherwise.
        """
        if storage_spec.key == 'ip' and storage_spec.value == specs.get('ip'):
            return True
        return bool(
            storage_spec.key == 'path'
            and storage_spec.value == specs.get('path')
        )

    def _check_specs_localfs_storage(self, specs_to_check: Dict) -> None:
        """Check if a storage with the given spec for LocalFS already exists.

        Args:
            specs_to_check (Dict): A dictionary containing the specifications
                for the LocalFS storage.

        Raises:
            StorageExistsError: If a storage with the given specifications
                already exists.
        """
        LOG.info('Checking if storage with the given specs exists...')
        unique_specs = ['path']
        for unique_spec_key in unique_specs:
            spec_to_check_value = specs_to_check.get(unique_spec_key)
            if spec_to_check_value is not None:
                existing_db_spec = self.uow.storages.get_spec_by_key_value(
                    unique_spec_key, spec_to_check_value
                )
                if existing_db_spec:
                    message = (
                        f'Storage {existing_db_spec.storage.id} already exists '
                        f'with {unique_spec_key}: {spec_to_check_value!r}.'
                    )
                    LOG.error(message)
                    raise exceptions.StorageExistsError(message)

    def _check_spec_exists_for_storage(
        self, specs: Dict, storage_type: str
    ) -> None:
        """Check if a storage with the given specifications already exists.

        Args:
            specs (Dict): A dictionary containing the specifications for the
                storage.
            storage_type (str): The type of storage ('nfs' or 'localfs').

        Raises:
            ValueError: If the provided storage type is invalid.
        """
        if not specs:
            return
        if storage_type == 'nfs':
            self._check_spec_exists_for_nfs_storage(specs)
        elif storage_type == 'localfs':
            self._check_specs_localfs_storage(specs)
        else:
            msg = f'Invalid storage type: {storage_type}'
            raise ValueError(msg)

    def _check_storage_has_no_objects(self, storage_id: str) -> None:
        """Check if the storage has any associated objects.

        Args:
            storage_id (str): The ID of the storage object to check.

        Raises:
            StorageHasObjects: If the storage contains at least one associated
            object.
        """
        volumes = self._get_volumes(storage_id)
        images = self._get_images(storage_id)
        templates = self._get_templates(storage_id)
        storage_objects = [
            ('volumes', [vol['name'] for vol in volumes]),
            ('images', [img['name'] for img in images]),
            ('templates', [tmp['name'] for tmp in templates]),
        ]

        existing_objects = [
            (entities_type, names)
            for entities_type, names in storage_objects
            if names
        ]
        if existing_objects:
            details = '\n'.join(
                f'{name}: {" ".join(names)}' for name, names in existing_objects
            )
            message: str = f'Storage {storage_id} has {details}'
            raise exceptions.StorageHasObjects(message)

    def _get_volumes(self, storage_id: str) -> List[Dict]:
        """Retrieve and return all volumes by storage id"""
        try:
            volumes = self.volume_service_client.get_all_volumes(
                {'storage_id': storage_id}
            )
        except RpcException as err:
            LOG.error(f'Error retrieving volumes: {err!s}')
            raise
        return volumes

    def _get_images(self, storage_id: str) -> List[Dict]:
        """Retrieve and return all images by storage id"""
        try:
            images = self.image_service_client.get_all_images(
                {'storage_id': storage_id}
            )
        except RpcException as err:
            LOG.error(f'Error retrieving images: {err!s}')
            raise
        return images

    def _get_templates(self, storage_id: str) -> List[Dict]:
        """Retrieve and return all templates by storage id"""
        try:
            all_templates = self.template_service_client.get_all_templates()
            storages_templates = [
                tmp for tmp in all_templates if tmp['storage_id'] == storage_id
            ]
        except RpcException as err:
            LOG.error(f'Error retrieving templates: {err!s}')
            raise
        return storages_templates

    def _check_device(self, device_path: str) -> None:
        """Check if the given device path is valid and not a system disk or part

        Args:
            device_path (str): The path of the device to check.

        Raises:
            DeviceDoesNotExist: If the device path does not exist.
            CannotCreateStorageOnRootOfSystemDisk: If the device is a system
                disk.
            CannotCreateStorageOnSystemPartition: If the device is a system
                partition.
        """
        local_disks = {
            device.get('path', ''): device
            for device in self.get_local_disks({})
        }

        if device_path not in local_disks:
            message = f"Device by path {device_path} doesn't exist."
            LOG.error(message)
            raise exceptions.DeviceDoesNotExist(message)

        device = local_disks[device_path]
        device_type = device.get('type')
        if device_type and is_system_disk(device_path):
            message = (
                f'This is system disk: {device_path}.'
                'Please specify a non-system partition'
            )
            LOG.error(message)
            raise exceptions.CannotCreateStorageOnRootOfSystemDisk(message)

        if device_type == 'part':
            parent_path = device.get('parent')
            part_num = device_path[len(parent_path) :]
            if is_system_partition(parent_path, part_num):
                message = (
                    f'This is system partition: {device_path}.'
                    'Please specify a non-system partition'
                )
                raise exceptions.CannotCreateStorageOnSystemPartition(message)

    @staticmethod
    def _check_storage_status(
        storage_status: str, available_statuses: List
    ) -> None:
        """Check if the storage status is valid ащк the given list of statuses.

        Args:
            storage_status (str): The current status of the storage.
            available_statuses (List): A list of valid storage statuses.

        Raises:
            StorageStatusError: If the storage status is not in the list of
                valid statuses.
        """
        if storage_status not in available_statuses:
            message = (
                f'Storage status is {storage_status} but '
                f'must be in {available_statuses}'
            )
            LOG.error(message)
            raise exceptions.StorageStatusError(message)

    def create_local_partition(self, data: Dict) -> Dict:
        """Create a new local partition on a disk.

        Args:
            data (Dict): A dictionary containing the following keys:
                - 'local_disk_path': Path to the local disk where the partition
                    will be created.
                - 'storage_type': Type of storage for the partition.
                - 'start': Starting point of the partition.
                - 'start_unit': Unit of measurement for the starting point.
                - 'end': Ending point of the partition.
                - 'end_unit': Unit of measurement for the ending point.

        Returns:
            Dict: A dictionary containing information about the newly created
                partition.

        Raises:
            StorageExistsError: If the provided disk path does not exist.
        """
        LOG.info('Start creating local partition.')

        local_disks = get_system_disks()
        local_disk_path = data.pop('local_disk_path')
        user_data = data.pop('user_data')

        local_disk = next(
            (
                disk
                for disk in local_disks
                if disk.get('path') == local_disk_path
            ),
            None,
        )
        if local_disk is None:
            msg = f'Storage path: "{local_disk_path}", does not exist.'
            raise exceptions.StorageExistsError(msg)

        data_for_manager = {
            'local_disk_path': local_disk_path,
            'storage_type': data.pop('storage_type'),
        }
        data_for_method = {
            'size_value': data.pop('size_value'),
            'size_unit': data.pop('size_unit'),
        }

        new_part_num = self.domain_rpc.call(
            base.BasePartition.create_partition.__name__,
            data_for_manager=data_for_manager,
            data_for_method=data_for_method,
        )

        local_parts_info = get_local_partitions()
        # search for information about the created partition by its name, which
        # is expected to be formed from {local_disk_path}{new_part_num}
        # for example (dev/sdb1)
        new_part = next(
            filter(
                lambda part: part.get('path')
                == f'{local_disk_path}{new_part_num}',
                local_parts_info,
            )
        )

        self.event_store.add_event(
            '',  # do not use uuid here
            user_data.get('id'),
            self.create_local_partition.__name__,
            (
                f"Partition {new_part.get('name')} was created on "
                f"disk {local_disk_path}"
            ),
        )

        LOG.info('Finish creating local partition.')
        return new_part

    def get_local_disk_partitions_info(self, data: Dict) -> Dict:
        """Get information about local disk partitions.

        This method collects information about partitions on the specified local
        disk.

        Args:
            data (Dict): A dictionary containing the following key:
                - 'disk_path': Path to the local disk.
                - 'unit': Unit for partition values

        Returns:
            Dict: A dictionary containing information about local disk
                partitions.

        """
        LOG.info('Starting collecting local disk partitions info.')
        parted_info: Dict = self.domain_rpc.call(
            base.BasePartition.get_partitions_info.__name__,
            data_for_manager={
                'local_disk_path': data.get('disk_path'),
                'storage_type': 'local_partition',
            },
        )
        LOG.info('Finish collecting local disk partitions info.')
        return parted_info

    def delete_local_partition(self, data: Dict) -> Dict:
        """Delete a local partition.

        This method deletes the specified local partition.

        Args:
            data (Dict): A dictionary containing the following keys:
                - 'parent_path': Path to the parent storage of the partition.
                - 'storage_type': Type of storage for the partition.
                - 'partition_number': Number of the partition to be deleted.

        Returns:
            Dict: A dictionary containing a message indicating the success of
                the operation.

        Raises:
            CannotDeleteSystemPartition: If the partition is a system partition.
            PartitionHasStorage: If the partition has associated storages.
        """
        LOG.info('Start deleting local partition.')
        disk_path = data.pop('local_disk_path')
        part_num = data.pop('partition_number')
        storage_type = data.pop('storage_type')
        user_data = data.pop('user_data')

        if is_system_partition(disk_path, part_num):
            msg = f'{disk_path}{part_num}'
            raise exceptions.CannotDeleteSystemPartition(msg)

        self._check_storages_on_partition(disk_path, part_num)

        self.domain_rpc.call(
            base.BasePartition.delete_partition.__name__,
            data_for_manager={
                'local_disk_path': disk_path,
                'storage_type': storage_type,
            },
            data_for_method={'partition_number': part_num},
        )

        self.event_store.add_event(
            data.get('partition_number', ''),
            user_data.get('id'),
            self.delete_local_partition.__name__,
            f'Partition {part_num} was deleted from disk {disk_path}',
        )

        LOG.info('Finish deleting local partition.')
        return {'message': 'partition successfully deleted.'}

    def _get_storages_on_partition(self, disk_path: str, part_num: str) -> List:
        """Get a list of storages associated with a partition.

        Args:
            disk_path (str): The path of the disk containing the partition.
            part_num (str): The number of the partition.

        Returns:
            List: A list of storage names associated with the partition.
        """
        partition_path = f'{disk_path}{part_num}'
        partition_storages = []
        with self.uow:
            db_storages = self.uow.storages.get_all()
            for db_storage in db_storages:
                storage_extra_specs = db_storage.extra_specs
                for storage_spec in storage_extra_specs:
                    spec_key = storage_spec.key
                    spec_value = storage_spec.value
                    if spec_key == 'path' and spec_value == partition_path:
                        partition_storages.append(db_storage.name)
        return partition_storages

    def _check_storages_on_partition(
        self, disk_path: str, part_num: str
    ) -> None:
        """Check if a partition has associated storages.

        Args:
            disk_path (str): The path of the disk containing the partition.
            part_num (str): The number of the partition.

        Raises:
            PartitionHasStorage: If the partition has associated storages.
        """
        storages_on_partition = self._get_storages_on_partition(
            disk_path, part_num
        )
        if storages_on_partition:
            message = (
                f'Please delete storages: {storages_on_partition} '
                'before deleting partition.'
            )
            raise exceptions.PartitionHasStorage(message)

    def create_storage(self, data: Dict) -> Dict:
        """Create a new storage.

        Args:
            data (Dict): A dictionary containing the storage name, type,
                specifications, and user data.

        Returns:
            Dict: A dictionary representing the serialized storage with its
                metadata.

        Raises:
            ValueError: If the provided storage type is invalid.
            StorageExistsError: If a storage with the same name or
                specifications already exists.
        """
        LOG.info('Starting create_storage service layer method.')
        user_info = data.pop('user_data', {})
        user_id = user_info.get('id', '')
        name = data.get('name', '')
        creating_path = data.get('specs', {}).get('path', '')
        data.update({'user_id': user_id})

        if data.get('storage_type', '') == 'localfs':
            self._check_device(creating_path)
            data['specs'].update({'fs_uuid': '', 'mount_point': ''})
        elif data.get('storage_type', '') == 'nfs':
            data['specs'].update({'mount_point': ''})
        else:
            msg = f"Invalid storage type: {data.get('storage_type')}"
            raise ValueError(msg)

        self._check_storage_exists_with_current_name(name)
        with self.uow:
            self._check_spec_exists_for_storage(
                data.get('specs', {}), data.get('storage_type', '')
            )
            db_storage = cast(orm.Storage, DataSerializer.to_db(data))
            db_storage.status = StorageStatus.new.name
            for key, value in data.get('specs', {}).items():
                spec = {
                    'key': key,
                    'value': str(value) if value else None,
                    'storage_id': db_storage.id,
                }
                db_spec = cast(
                    orm.StorageExtraSpecs,
                    DataSerializer.to_db(spec, orm.StorageExtraSpecs),
                )
                db_storage.extra_specs.append(db_spec)
            self.uow.storages.add(db_storage)
            self.uow.commit()
            LOG.info(f'Storage {name} inserted into db: {db_storage}.')

        domain_storage = DataSerializer.to_domain(db_storage)
        web_storage = DataSerializer.to_web(db_storage)
        LOG.debug('Serialized db storage for web: %s.' % web_storage)
        LOG.info('Cast service layer on _create_storage asynchron.')
        self.service_layer_rpc.cast(
            self._create_storage.__name__, data_for_method=domain_storage
        )
        self.event_store.add_event(
            web_storage.get('id', ''),
            user_id,
            self.create_storage.__name__,
            'Storage successfully inserted into db.',
        )
        LOG.info('Service layer method create_storage executed successfully.')
        return web_storage

    def _create_storage(self, storage_info: Dict) -> None:
        """Create a new storage

        Creates a storage in the database and then calls the domain
        manager to create the corresponding storage.

        Args:
            storage_info (Dict): A dictionary containing the storage information

        Raises:
            RpcCallException: If there is an exception raised while
                making a remote procedure call to the domain's domain manager.

        Returns:
            None.

        When creating a new storage in the system, this method
        first modifies the status of the storage in the database
        to 'creating' after ensuring it is in the correct status.
        Then, a remote procedure call (RPC) is made to the domain's
        domain manager to create the storage. If the RPC is successful,
        the status of the storage in the database is modified to
        'available', the size of the storage is updated, along with
        its availability, and any associated extra specifications
        such as mount points that are returned by the domain manager.

        If the creation of the storage fails, the status of the storage
        in the database is modified to 'error' with the error message
        related to the failure. The error message is also recorded in
        the event store. Finally, the failed RPC call is re-raised so
        that it can be handled further upstream.
        """
        LOG.info('Service layer is handling response on _create_storage.')
        with self.uow:
            db_storage = self.uow.storages.get(storage_info.get('id', ''))
            self._check_storage_status(
                db_storage.status, [StorageStatus.new.name]
            )
            db_storage.status = StorageStatus.creating.name
            self.uow.commit()
            LOG.info(
                'Db storage status was updated on %s.'
                % StorageStatus.creating.name
            )
            try:
                domain_storage = self.domain_rpc.call(
                    base.BaseStorage.create.__name__,
                    data_for_manager=storage_info,
                    time_limit=180,
                    priority=10,
                )
                LOG.debug('Domain manager return result: %s.' % domain_storage)
                db_storage.status = StorageStatus.available.name
                db_storage.size = domain_storage.get('size')
                db_storage.available = domain_storage.get('available')
                db_storage.initialized = True
                LOG.info(
                    'Db storage status was updated on %s.'
                    % StorageStatus.available.name
                )
                for spec in db_storage.extra_specs:
                    if spec.key == 'mount_point':
                        spec.value = domain_storage.get('mount_point')
                    if spec.key == 'fs_uuid':
                        spec.value = domain_storage.get('fs_uuid')
                LOG.info(
                    'Extra specs was added for storage: %s.' % db_storage.id
                )
                self.event_store.add_event(
                    str(db_storage.id),
                    str(db_storage.user_id),
                    self.create_storage.__name__,
                    'Storage successfully created in the system.',
                )
            except RpcCallException as err:
                message = (
                    'While creating storage in the system '
                    f'handle error: {err!s}'
                )
                db_storage.status = StorageStatus.error.name
                db_storage.information = message
                LOG.error(message)
                self.event_store.add_event(
                    str(db_storage.id),
                    str(db_storage.user_id),
                    self.create_storage.__name__,
                    message,
                )
                raise
            finally:
                self.uow.commit()
        LOG.info(
            'Service layer method _create_storage was ' 'successfully processed'
        )

    def delete_storage(self, data: Dict) -> Dict:
        """Deletes a storage from the database and from the system.

        Args:
            data (Dict): A dictionary containing the storage ID and user data.

        Returns:
            Dict: A dictionary representing the serialized storage with its
                metadata.

        Raises:
            StorageHasVolumesOrImages: If the storage has associated volumes or
                images.
        """
        LOG.info('Service layer start handling response on delete storage.')
        user_info = data.pop('user_data', {})
        storage_id: str = data['storage_id']

        with self.uow:
            db_storage = self.uow.storages.get(uuid.UUID(storage_id))
            try:
                self._check_storage_has_no_objects(storage_id)
            except exceptions.StorageHasObjects as err:
                LOG.error(str(err))
                self.event_store.add_event(
                    str(db_storage.id),
                    str(db_storage.user_id),
                    self.delete_storage.__name__,
                    str(err),
                )
                raise
            db_storage.status = StorageStatus.deleting.name
            domain_storage = DataSerializer.to_domain(db_storage)
            self.uow.commit()
            domain_storage.update({'user_info': user_info})
        LOG.info('Cast service layer on _delete_storage asynchronous.')
        self.service_layer_rpc.cast(
            self._delete_storage.__name__,
            data_for_method=domain_storage,
            priority=8,
        )
        LOG.info(
            'Service layer method delete storage was successfully processed'
        )
        return DataSerializer.to_web(db_storage)

    def _delete_storage(self, domain_storage: Dict) -> None:
        """Asynchronous method to delete a storage from the system.

        Args:
            domain_storage (Dict): A dictionary containing the storage
                information.

        Raises:
            RpcCallException: If an error occurs during the storage deletion
                process.
            RpcCallTimeoutException: If the RPC call times out during the
                storage deletion process.
        """
        LOG.info('Service layer start handling response on _delete storage.')
        domain_storage.pop('user_info', {})
        storage_id = domain_storage.get('id', '')
        with self.uow:
            db_storage = self.uow.storages.get(storage_id)
            LOG.debug('Got storage: %s from db.' % domain_storage)
            try:
                self._check_storage_has_no_objects(str(storage_id))
                LOG.info('Call domain layer on delete storage.')
                result = self.domain_rpc.call(
                    base.BaseStorage.delete.__name__,
                    data_for_manager=domain_storage,
                    time_limit=180,
                    priority=10,
                )
                LOG.debug('Domain manager return result: %s.' % result)
                LOG.info('Storage: %s deleted from system.' % storage_id)
                self.uow.storages.delete(storage_id)
                LOG.info('Storage: %s deleted from db.' % storage_id)
                self.event_store.add_event(
                    str(db_storage.id),
                    str(db_storage.user_id),
                    self.delete_storage.__name__,
                    'Storage successfully deleted from the system and db.',
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                db_storage.status = StorageStatus.error.name
                db_storage.information = str(err)
                LOG.error(str(err))
                self.event_store.add_event(
                    str(db_storage.id),
                    str(db_storage.user_id),
                    self._delete_storage.__name__,
                    str(err),
                )
            finally:
                self.uow.commit()
        LOG.info(
            'Service layer method _delete storage ' 'was successfully processed'
        )

    def get_local_disks(self, data: Dict) -> List:
        """Retrieve a list of local disks and partitions.

        Args:
            data (Dict): A dictionary containing a flag to include only free
                local disks.

        Returns:
            List: A list of dictionaries representing the available local disks
                and partitions.
        """
        LOG.info('Start searching for local disks.')

        flag_free_local_disks = data.get('free_local_disks', False)
        system_disks = get_system_disks()
        available_disks = []
        with self.uow:
            for disk in system_disks:
                spec = self.uow.storages.filter_extra_specs(
                    all_rows=False, value=disk['path']
                )
                if flag_free_local_disks:
                    if not spec:
                        available_disks.append(disk)
                    else:
                        continue
                else:
                    available_disks.append(disk)

        partitions = get_local_partitions()
        return available_disks + partitions

    @periodic_task(interval=10)
    def monitoring(self) -> None:
        """Method for periodic monitoring of storages.

        This method is responsible for periodically monitoring the status of
        storages in the system. It retrieves all storages from the database,
        checks their status and availability, and then updates the storage
        information accordingly.

        The method performs the following steps:

        1. Get all storages from the database and convert them to domain objects
        2. For each storage:
        - Validate the storage status and availability.
        - Get updated storage information from the domain.
        - Update the storage information in a list for subsequent database
            update.
        - Handle any exceptions that may occur during the process.
        3. Update the storage information in the database.

        This method is designed to run periodically using the `@periodic_task`
        decorator with an interval of 10 seconds.
        """
        LOG.info('Start monitoring.')
        domain_storages = self._collect_serialized_storages()
        if not domain_storages:
            LOG.info("Stop monitoring. Storages don't exist.")
            return

        updated_storages = []
        for domain_storage in domain_storages:
            try:
                self._validate_storage_status(domain_storage)
                updated_storage = self._get_updated_storage_info(domain_storage)
                updated_storages.append(updated_storage)
            except exceptions.StorageStatusError:
                LOG.info(
                    f'Monitoring not update status for '
                    f'{domain_storage.get("name")} because has '
                    f'{domain_storage.get("status")}'
                )
            except (
                RpcCallException,
                RpcCallTimeoutException,
                exceptions.GetEmptyDomainStorageInfo,
            ) as err:
                updated_storage = self._handle_monitoring_error(
                    domain_storage, err
                )
                updated_storages.append(updated_storage)

        self._update_all_storages(updated_storages)
        LOG.info('Stop monitoring.')

    def _validate_storage_status(self, domain_storage: Dict) -> None:
        """Validate the storage status before monitoring.

        Args:
            domain_storage (Dict): A dictionary representing the storage
                information.

        Raises:
            StorageStatusError: If the storage status is not valid for
                monitoring.
        """
        monitoring_statuses = [status.name for status in StorageStatus]
        self._check_storage_status(
            domain_storage.get('status', ''), monitoring_statuses
        )

    def _get_updated_storage_info(self, domain_storage: Dict) -> Dict:
        """Get updated storage information from the domain layer.

        Args:
            domain_storage (Dict): A dictionary representing the storage
                information.

        Returns:
            Dict: A dictionary containing the updated storage information.

        Raises:
            RpcCallException: If an error occurs during the RPC call to the
                domain layer.
            RpcCallTimeoutException: If the RPC call to the domain layer times
                out.
        """
        storage_info = self.domain_rpc.call(
            base.BaseStorage.do_setup.__name__,
            data_for_manager=domain_storage,
            time_limit=180,
            priority=5,
        )
        return self._get_updated_storage_info_for_db(storage_info)

    def _handle_monitoring_error(
        self, domain_storage: Dict, err: Exception
    ) -> Dict:
        """Handle errors that occur during storage monitoring.

        Args:
            domain_storage (Dict): A dictionary representing the storage
                information.
            err (Exception): The exception that occurred during monitoring.

        Returns:
            Dict: A dictionary containing the updated storage information with
                an error status and message.
        """
        message = self._get_monitoring_error_message(err, domain_storage)
        LOG.error(message)
        return {
            'id': domain_storage.get('id'),
            'status': StorageStatus.error.name,
            'information': message,
        }

    def _get_monitoring_error_message(
        self, err: Exception, domain_storage: Dict
    ) -> str:
        """Get the error message for a monitoring error.

        Args:
            err (Exception): The exception that occurred during monitoring.
            domain_storage (Dict): A dictionary representing the storage
                information.

        Returns:
            str: The error message.
        """
        if isinstance(err, (RpcCallException, RpcCallTimeoutException)):
            return (
                f"Handle error: {err!s} while monitoring storage "
                f"{domain_storage.get('name', '')}."
            )
        if isinstance(err, exceptions.GetEmptyDomainStorageInfo):
            return str(err)
        if isinstance(err, exceptions.StorageStatusError):
            return (
                f"Handle error: {err!s} while monitoring storage "
                f"{domain_storage.get('name', '')}."
            )
        return str(err)

    def _get_local_disk_by_fs_uuid(self, fs_uuid: str) -> Dict:
        """Retrieve a local disk by its file system UUID.

        Args:
            fs_uuid (str): The file system UUID of the local disk.

        Returns:
            Dict: A dictionary representing the local disk information, or an
                empty dictionary if not found.
        """
        local_disks: List[Dict] = self.get_local_disks({})
        for disk in local_disks:
            if disk.get('fs_uuid') == fs_uuid:
                return disk
        return {}

    def _collect_serialized_storages(self) -> List:
        """Collect and serialize all storages from the database.

        Returns:
            List: A list of dictionaries representing the serialized storages.
        """
        serialized_storages = []
        with self.uow:
            for db_storage in self.uow.storages.get_all():
                domain_storage = DataSerializer.to_domain(db_storage)
                if db_storage.storage_type == 'localfs':
                    fs_uuid = domain_storage.get('fs_uuid', '')
                    disk = self._get_local_disk_by_fs_uuid(fs_uuid)
                    if disk.get('path', ''):
                        domain_storage.update({'path': disk.get('path', '')})
                serialized_storages.append(domain_storage)
        return serialized_storages

    @staticmethod
    def _get_updated_storage_info_for_db(storage_info: Dict) -> Dict:
        """Get updated storage information for the def.

        Args:
            storage_info (Dict): A dictionary containing the updated storage
                information from the domain layer.

        Returns:
            Dict: A dictionary containing the updated storage information for
                the database.

        Raises:
            GetEmptyDomainStorageInfo: If the provided storage information is
                empty.
        """
        if not storage_info:
            message = 'Get empty domain storage information.'
            LOG.error(message)
            raise exceptions.GetEmptyDomainStorageInfo(message)

        updated_storage = {
            'id': storage_info.get('id'),
            'size': storage_info.get('size', 0),
            'available': storage_info.get('available', 0),
            'status': StorageStatus.available.name,
            'initialized': storage_info.get('initialized', False),
            'information': '',
            'extra_specs': [],
        }

        if storage_info.get('mount_point', ''):
            updated_storage['extra_specs'].append(
                {'mount_point': storage_info.get('mount_point')}
            )

        if storage_info.get('path', ''):
            updated_storage['extra_specs'].append(
                {'path': storage_info.get('path')}
            )

        return updated_storage

    def _update_all_storages(self, storages: List) -> None:
        """Update all storages in the database.

        Args:
            storages (List): A list of dictionaries representing the updated
                storage information.
        """
        list_of_extra_specs = []
        for storage in storages:
            extra_specs = storage.pop('extra_specs', [])
            for spec in extra_specs:
                key, value = next(iter(spec.items()))
                list_of_extra_specs.append(
                    {
                        'key': key,
                        'value': value,
                        'storage_id': storage.get('id'),
                    }
                )
        with self.uow:
            with synchronized_session(self.uow.session):
                self.uow.storages.bulk_update(storages)
                for spec in list_of_extra_specs:
                    self.uow.storages.update_spec_by_key_for_storage(**spec)
            self.uow.commit()
