"""Module for managing virtual machine operations in the service layer.

This module defines the `VMServiceLayerManager` class, which is responsible
for handling the core business logic related to virtual machine operations.
The class interacts with various components, such as the domain layer,
RPC clients, and the database, to perform actions like creating, deleting,
starting, and editing virtual machines.

Classes:
    VMServiceLayerManager: Manager class for handling virtual machine
        operations in the service layer.

Enums:
    VmStatus: Enumeration of possible virtual machine statuses.
    VmPowerState: Enumeration of possible virtual machine power states.
    DiskType: Enumeration of disk types used in virtual machines.

Functions:
    get_vm: Retrieve a virtual machine by ID.
    get_all_vms: Retrieve all virtual machines.
    create_vm: Create a new virtual machine.
    delete_vm: Delete a virtual machine by ID.
    start_vm: Start a virtual machine by ID.
    shut_off_vm: Shut off a virtual machine by ID.
    edit_vm: Edit a virtual machine by ID.
    vnc: Access the VNC session of a virtual machine.
    monitoring: Periodically monitor the state of virtual machines.
"""

from __future__ import annotations

import enum
import time
import string
from uuid import UUID, uuid4
from typing import Dict, List, Optional, cast
from collections import namedtuple

from openvair.libs.log import get_logger
from openvair.libs.libvirt.vm import get_vms_state
from openvair.modules.tools.utils import synchronized_session
from openvair.modules.base_manager import BackgroundTasks, periodic_task
from openvair.modules.virtual_machines import config
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcServerInitializedException,
)
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.virtual_machines.adapters import orm
from openvair.libs.data_handlers.json.serializer import serialize_json
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.virtual_machines.domain.base import BaseVMDriver
from openvair.modules.virtual_machines.service_layer import (
    exceptions,
    unit_of_work,
)
from openvair.modules.virtual_machines.adapters.serializer import DataSerializer
from openvair.libs.messaging.clients.rpc_clients.image_rpc_client import (
    ImageServiceLayerRPCClient,
)
from openvair.libs.messaging.clients.rpc_clients.volume_rpc_client import (
    VolumeServiceLayerRPCClient,
)

LOG = get_logger(__name__)


CreateVmInfo = namedtuple(
    'CreateVmInfo',
    [
        'name',
        'description',
        'user_id',
        'status',
        'power_state',
        'cpu',
        'ram',
        'os',
        'graphic_interface',
        'attach_volumes',
        'attach_images',
        'auto_create_volumes',
        'virtual_interfaces',
    ],
)

EditVmInfo = namedtuple(
    'EditVmInfo',
    [
        'id',
        'name',
        'description',
        'cpu',
        'ram',
        'os',
        'graphic_interface',
        'attach_volumes',
        'attach_images',
        'auto_create_volumes',
        'detach_disks',
        'edit_disks',
        'new_virtual_interfaces',
        'detach_virtual_interfaces',
        'edit_virtual_interfaces',
    ],
)


class VmStatus(enum.Enum):
    """Enumeration of possible virtual machine statuses."""

    new = 1
    creating = 2
    creating_disks = 3
    attaching_disks = 4
    available = 5
    error = 6
    detaching_disks = 7
    deleting = 8
    corrupted = 9
    starting = 10
    shut_offing = 11
    editing = 12


class VmPowerState(enum.Enum):
    """Enumeration of possible virtual machine power states."""

    running = 1
    idle = 2
    paused = 3
    shut_off = 4
    crashed = 5
    suspended = 6


class DiskType(enum.Enum):
    """Enumeration of disk types used in virtual machines."""

    volume = 1
    image = 2


class VMServiceLayerManager(BackgroundTasks):
    """Manager class for handling virtual machine operations in service layer.

    This class provides methods for managing the lifecycle of virtual machines,
    including creation, deletion, starting, shutting off, and editing. It
    interacts with various services and the domain layer to ensure that
    operations are carried out correctly and in the right order.

    Attributes:
        uow (SqlAlchemyUnitOfWork): The unit of work for managing database
            transactions.
        domain_rpc (Protocol): The RPC client for communicating with the domain
            layer.
        service_layer_rpc (Protocol): The RPC client for communicating with
            other service layers.
        volume_service_client (VolumeServiceLayerProtocolInterface): The client
            for volume-related operations.
        image_service_client (ImageServiceLayerProtocolInterface): The client
            for image-related operations.
        event_store (EventCrud): The event store for logging VM events.
    """

    def __init__(self) -> None:
        """Initialize the VMServiceLayerManager.

        This constructor sets up the necessary components for managing
        virtual machines, including the unit of work, RPC clients,
        and event store.
        """
        super(VMServiceLayerManager, self).__init__()
        self.uow = unit_of_work.SqlAlchemyUnitOfWork()
        self.domain_rpc = MessagingClient(
            queue_name=config.SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=config.API_SERVICE_LAYER_QUEUE_NAME
        )
        self.volume_service_client = VolumeServiceLayerRPCClient()
        self.image_service_client = ImageServiceLayerRPCClient()
        self.event_store = EventCrud('virtual_machines')

    def get_vm(self, data: Dict) -> Dict:
        """Retrieve a virtual machine by ID.

        Args:
            data (Dict): The data containing the ID of the virtual machine
                to retrieve.

        Returns:
            Dict: The serialized virtual machine data.

        Raises:
            UnexpectedDataArguments: If the VM ID is not provided.
        """
        LOG.info('Service layer start handling response on get vm.')
        vm_id = data.pop('vm_id', '')
        if not vm_id:
            message = (
                f'Incorrect arguments were received'
                f'in the request get vm: {data}.'
            )
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        with self.uow:
            db_virtual_machine = self.uow.virtual_machines.get(vm_id)
            serialized_vm = DataSerializer.vm_to_web(db_virtual_machine)
            LOG.info(f'Got vm from db: {serialized_vm}.')
        LOG.info('Service layer method get vm was successfully processed.')
        return serialized_vm

    def get_all_vms(self) -> List:
        """Retrieve all virtual machines.

        Returns:
            List: A list of serialized virtual machine data.
        """
        LOG.info('Service layer start handling response on get vms.')
        with self.uow:
            db_virtual_machines = self.uow.virtual_machines.get_all()
            serialized_vms = [
                DataSerializer.vm_to_web(vm) for vm in db_virtual_machines
            ]
        LOG.info('Service layer method get all vms was successfully processed.')
        return serialized_vms

    @staticmethod
    def _prepare_create_vm_info(vm_info: Dict) -> CreateVmInfo:
        """Prepare the information needed to create a virtual machine.

        Args:
            vm_info (Dict): The dictionary containing the parameters
                of the virtual machine.

        Returns:
            CreateVmInfo: The prepared virtual machine information.
        """
        LOG.info('Preparing vm information for create.')
        user_info = vm_info.get('user_info', {})
        create_vm_info = CreateVmInfo(
            name=vm_info.pop('name', ''),
            description=vm_info.pop('description', ''),
            user_id=UUID(vm_info.pop('user_info', {}).get('id')),
            status=VmStatus.new.name,
            power_state=VmPowerState.shut_off.name,
            cpu=vm_info.pop('cpu', {}),
            ram=vm_info.pop('ram', {}),
            os=vm_info.pop('os', {}),
            graphic_interface=vm_info.pop('graphic_interface', {}),
            attach_volumes=[],
            attach_images=[],
            auto_create_volumes=[],
            virtual_interfaces=vm_info.pop('virtual_interfaces', []),
        )

        disks = vm_info.pop('disks', {})
        for attach_disk in disks.pop('attach_disks', []):
            attach_disk.update({'qos': serialize_json(attach_disk.get('qos'))})
            if attach_disk.get('volume_id', ''):
                attach_disk.update(
                    {
                        'type': DiskType.volume.value,
                        'disk_id': attach_disk.get('volume_id', ''),
                        'read_only': attach_disk.get('read_only', False),
                    }
                )
                create_vm_info.attach_volumes.append(attach_disk)
            elif attach_disk.get('image_id', ''):
                attach_disk.update(
                    {
                        'type': DiskType.image.value,
                        'disk_id': attach_disk.get('image_id', ''),
                        'read_only': True,
                    }
                )
                create_vm_info.attach_images.append(attach_disk)
            elif attach_disk.get('storage_id', ''):
                attach_disk.update({'user_info': user_info})
                create_vm_info.auto_create_volumes.append(attach_disk)
        LOG.info('Vm information was successfully prepared for creating.')
        return create_vm_info

    def _insert_vm_into_db(self, create_vm_info: CreateVmInfo) -> Dict:
        """Insert virtual machine information into the database.

        Args:
            create_vm_info (CreateVmInfo): The virtual machine information
                to insert.

        Returns:
            Dict: The serialized virtual machine data.
        """
        LOG.info('Inserting vm information into database.')
        with self.uow:
            db_vm = cast(
                orm.VirtualMachines,
                DataSerializer.to_db(
                    create_vm_info._asdict(), orm.VirtualMachines
                ),
            )

            db_vm.cpu = cast(
                orm.CpuInfo,
                DataSerializer.to_db(
                    create_vm_info.cpu,
                    orm.CpuInfo,
                ),
            )

            db_vm.ram = cast(
                orm.RAM,
                DataSerializer.to_db(create_vm_info.ram, orm.RAM),
            )

            db_vm.os = cast(
                orm.Os,
                DataSerializer.to_db(create_vm_info.os, orm.Os),
            )

            db_vm.graphic_interface = cast(
                orm.ProtocolGraphicInterface,
                DataSerializer.to_db(
                    create_vm_info.graphic_interface,
                    orm.ProtocolGraphicInterface,
                ),
            )
            LOG.info(f'Inserted graphic interface: {db_vm.graphic_interface}')

            for virt_interface in create_vm_info.virtual_interfaces:
                db_vm.virtual_interfaces.append(
                    cast(
                        orm.VirtualInterface,
                        DataSerializer.to_db(
                            virt_interface, orm.VirtualInterface
                        ),
                    )
                )

            self.uow.virtual_machines.add(db_vm)
            self.uow.commit()
            LOG.info('Vm was successfully inserted into database.')
            return DataSerializer.vm_to_web(db_vm)

    def create_vm(self, data: Dict) -> Dict:
        """Create a new virtual machine.

        Args:
            data (Dict): The data required to create the virtual machine.

        Returns:
            Dict: The serialized virtual machine data.
        """
        LOG.info('Handling call on create vm.')
        user_info: Dict = data.get('user_info', {})
        create_vm_info = self._prepare_create_vm_info(data)
        web_vm = self._insert_vm_into_db(create_vm_info)
        self.event_store.add_event(
            str(web_vm.get('id', '')),
            str(user_info.get('id,', '')),
            self.create_vm.__name__,
            f"VM {web_vm.get('name')} was successfully inserted into DB.",
        )

        self.service_layer_rpc.cast(
            self._create_vm.__name__,
            data_for_method={
                'vm_id': web_vm['id'],
                'attach_volumes': create_vm_info.attach_volumes,
                'attach_images': create_vm_info.attach_images,
                'auto_create_volumes': create_vm_info.auto_create_volumes,
                'user_info': user_info,
            },
        )
        LOG.info('Call on create vm was successfully processed.')
        return web_vm

    def _expect_volume_availability(self, volume_id: str) -> Dict:
        """Wait for a volume to become available.

        This method repeatedly checks the availability status of a volume until
        it becomes available or an error occurs. It raises exceptions if the
        maximum number of attempts is reached, if the volume information is
        empty, or if the volume status is "error".

        Args:
            volume_id (str): The ID of the volume to check.

        Returns:
            Dict: The volume information if the volume becomes available.
        """
        LOG.info('Expecting while volume will be available.')
        counter = 0
        max_count = 10
        while True:
            self._check_max_attempts(counter, max_count)
            time.sleep(1)

            volume = self._get_volume_info(volume_id)
            self._check_volume_status(volume)

            if volume.get('status') == 'available':
                LOG.info('Volume status is available')
                return volume

            counter += 1

    def _check_max_attempts(self, counter: int, max_count: int) -> None:
        """Check if the maximum number of attempts is reached.

        This method checks whether the number of attempts to check the volume
        status has reached the specified maximum. If the maximum is reached, it
        raises a `MaxTriesError`.

        Args:
            counter (int): The current number of attempts.
            max_count (int): The maximum number of allowed attempts.

        Raises:
            MaxTriesError: If the number of attempts exceeds the allowed
                maximum.
        """
        if counter >= max_count:
            message = 'The maximum number of attempts was completed.'
            LOG.error(message)
            raise exceptions.MaxTriesError(message)

    def _get_volume_info(self, volume_id: str) -> Dict:
        """Retrieve volume information and check if it is empty.

        This method fetches the volume information using the provided volume ID.
        If the retrieved volume information is empty, it raises a
        `ComesEmptyVolumeInfo` exception.

        Args:
            volume_id (str): The ID of the volume to retrieve information for.

        Returns:
            Dict: The retrieved volume information.

        Raises:
            ComesEmptyVolumeInfo: If the retrieved volume information is empty.
        """
        volume = self.volume_service_client.get_volume({'volume_id': volume_id})
        if not volume:
            message = 'Comes empty volume info.'
            LOG.error(message)
            raise exceptions.ComesEmptyVolumeInfo(message)
        return volume

    def _check_volume_status(self, volume: Dict) -> None:
        """Check the status of the volume.

        This method checks the status of the provided volume. If the status is
        "error", it raises a `VolumeStatusIsError` exception.

        Args:
            volume (Dict): The volume information dictionary containing the
                status to check.

        Raises:
            VolumeStatusIsError: If the volume status is "error".
        """
        if volume.get('status') == 'error':
            message = 'Volume status is error.'
            LOG.error(message)
            raise exceptions.VolumeStatusIsError(message)

    def _create_volumes(self, vm_name: str, volumes: List) -> List:
        """Create volumes for a virtual machine.

        Args:
            vm_name (str): The name of the virtual machine.
            volumes (List): A list of volume specifications.

        Returns:
            List: A list of created volumes.
        """
        LOG.info('Creating volumes.')
        auto_created_volumes = []
        for volume in volumes:
            volume_name = volume.get('name', None)
            creating_volume = self.volume_service_client.create_volume(
                {
                    'name': volume_name or str(uuid4()),
                    'description': f'auto created volume for {vm_name}.',
                    'format': volume.get('format', 'qcow2'),
                    'size': volume.pop('size', '0'),
                    'storage_id': volume.pop('storage_id', ''),
                    'user_info': volume.get('user_info'),
                    'read_only': volume.pop('read_only'),
                }
            )
            try:
                available_volume = self._expect_volume_availability(
                    creating_volume.get('id', '')
                )
            except (
                exceptions.MaxTriesError,
                exceptions.ComesEmptyVolumeInfo,
                exceptions.VolumeStatusIsError,
            ) as err:
                message = (
                    'While expecting volume availability '
                    f'catch error: {err!s}'
                )
                LOG.error(message)
                continue

            available_volume.update(volume)
            available_volume.update(
                {
                    'disk_id': available_volume.get('id'),
                    'type': DiskType.volume.value,
                    'read_only': available_volume.get('read_only', False),
                }
            )
            available_volume.pop('id')
            auto_created_volumes.append(available_volume)
        LOG.info('Volumes was successfully created.')
        return auto_created_volumes

    def _attach_image_to_vm(self, image_id: str, vm_id: str) -> Dict:
        """Attach an image to a virtual machine.

        Args:
            image_id (str): The ID of the image to attach.
            vm_id (str): The ID of the virtual machine.

        Returns:
            Dict: The attachment information.
        """
        LOG.info('Sending request on attach image to vm.')
        attach_info = self.image_service_client.attach_image(
            {'image_id': image_id, 'vm_id': vm_id}
        )
        LOG.info('Image was successfully attached to vm.')
        return attach_info

    def _attach_volume_to_vm(self, volume_id: str, vm_id: str) -> Dict:
        """Attach a volume to a virtual machine.

        Args:
            volume_id (str): The ID of the volume to attach.
            vm_id (str): The ID of the virtual machine.

        Returns:
            Dict: The attachment information.
        """
        LOG.info('Sending request on attach volume to vm.')
        attach_info = self.volume_service_client.attach_volume(
            {'volume_id': volume_id, 'vm_id': vm_id}
        )
        LOG.info('Volume was successfully attached to vm.')
        return attach_info

    def _attach_disk_to_vm(self, vm_id: str, disk: Dict) -> Dict:
        """Attach a disk to a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.
            disk (Dict): The disk information.

        Returns:
            Dict: The updated disk information.

        Raises:
            UnexpectedDataArguments: If the disk type is unexpected.
        """
        LOG.info('Attaching disk to vm.')
        disk_type = disk.get('type', '')
        if disk_type == DiskType.image.value:
            attach_info = self._attach_image_to_vm(
                disk.get('image_id', ''), vm_id
            )
        elif disk_type == DiskType.volume.value:
            attach_info = self._attach_volume_to_vm(
                disk.get('disk_id', ''), vm_id
            )
        else:
            message = 'Unexpected disk type.'
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        disk.update(
            {
                'path': attach_info.get('path', ''),
                'size': int(attach_info.get('size', 0)),
                'provisioning': attach_info.get('provisioning', ''),
            }
        )
        LOG.info('Disk was successfully attached to vm.')
        return disk

    def _add_disks_to_vm(self, vm_id: str, disks: List) -> None:
        """Attach a list of disks to a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.
            disks (List): The list of disks to attach.
        """
        LOG.info(
            'Start requesting on attach disks to vm and insert it into db.'
        )
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            for disk in disks:
                try:
                    attached_disk = self._attach_disk_to_vm(vm_id, disk)
                    db_vm.disks.append(
                        cast(
                            orm.Disk,
                            DataSerializer.to_db(attached_disk, orm.Disk),
                        )
                    )
                except exceptions.UnexpectedDataArguments as err:
                    message = (
                        'While attaching disks to vm '
                        f'was raised err: {err!s}'
                    )
                    LOG.error(message)
            self.uow.commit()
        LOG.info('Disks was successfully attached and inserted into db.')

    def _create_vm(self, data: Dict) -> None:
        """Create a virtual machine and attach disks to it.

        Args:
            data (Dict): The data required to create the virtual machine.
        """
        LOG.info('Handling response on _create_vm.')
        vm_id = data.pop('vm_id', '')
        user_info = data.pop('user_info', {})
        attach_volumes = data.pop('attach_volumes', [])
        attach_images = data.pop('attach_images', [])
        auto_create_volumes = data.pop('auto_create_volumes', [])

        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            LOG.info(f'VM info before processing: {db_vm.__dict__}')

            if auto_create_volumes:
                created_disks = self._create_volumes(
                    db_vm.name, auto_create_volumes
                )
                attach_volumes.extend(created_disks)

        self._add_disks_to_vm(vm_id, attach_volumes + attach_images)
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            LOG.info(f'VM info after processing: {db_vm.__dict__}')

            db_vm.status = VmStatus.available.name
            self.uow.commit()

        self.event_store.add_event(
            str(db_vm.id),
            user_info.get('id'),
            self._create_vm.__name__,
            f'VM {db_vm.name} was successfully created.',
        )
        LOG.info('Response on _create_vm was successfully processed.')

    @staticmethod
    def _check_vm_status(vm_status: str, available_statuses: List) -> None:
        """Check if the VM status is in the list of available statuses.

        Args:
            vm_status (str): The current status of the VM.
            available_statuses (List): A list of available statuses.

        Raises:
            VMStatusException: If the VM status is not in the list
                of available statuses.
        """
        LOG.info('Checking vm status on availability.')
        if vm_status not in available_statuses:
            message = (
                f"Vm status is {vm_status}, but must be "
                f"in {', '.join(available_statuses)}."
            )
            LOG.error(message)
            raise exceptions.VMStatusException(message)
        LOG.info('Vm status was successfully checked.')

    @staticmethod
    def _check_vm_power_state(
        vm_power_state: str, available_states: List
    ) -> None:
        """Check if the VM power state is in the list of available states.

        Args:
            vm_power_state (str): The current power state of the VM.
            available_states (List): A list of available power states.

        Raises:
            VMPowerStateException: If the VM power state is not in the list
                of available power states.
        """
        LOG.info('Checking vm power state on availability.')
        if vm_power_state not in available_states:
            message = (
                f"Vm power state is {vm_power_state}, but must "
                f"be in {', '.join(available_states)}"
            )
            LOG.error(message)
            raise exceptions.VMPowerStateException(message)
        LOG.info('Vm power state was successfully checked.')

    def _detach_image_from_vm(self, vm_id: str, image_id: str) -> None:
        """Detach an image from a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.
            image_id (str): The ID of the image to detach.
        """
        LOG.info('Sending request on detach image from vm.')
        self.image_service_client.detach_image(
            {'image_id': image_id, 'vm_id': vm_id}
        )
        LOG.info('Image was successfully detached from vm.')

    def _detach_volume_from_vm(self, vm_id: str, volume_id: str) -> None:
        """Detach a volume from a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.
            volume_id (str): The ID of the volume to detach.
        """
        LOG.info('Sending request on detach volume from vm.')
        self.volume_service_client.detach_volume(
            {'volume_id': volume_id, 'vm_id': vm_id}
        )
        LOG.info('Volume was successfully detached from vm.')

    def _detach_disk_from_vm(self, vm_id: str, disk: Dict) -> None:
        """Detach a disk from a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.
            disk (Dict): The disk information.

        Raises:
            UnexpectedDataArguments: If the disk type is unexpected.
        """
        LOG.info('Detaching disk from vm.')
        disk_type = disk.get('type', '')
        disk_id = disk.get('disk_id', '')
        if disk_type == DiskType.image.value:
            self._detach_image_from_vm(vm_id, disk_id)
        elif disk_type == DiskType.volume.value:
            self._detach_volume_from_vm(vm_id, disk_id)
        else:
            message = 'Unexpected disk type.'
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        LOG.info('Disk was successfully detached from vm.')

    def _detach_disks_from_vm(self, disks: List) -> None:
        """Detach and delete disks from a virtual machine.

        Args:
            disks (List): A list of disks to detach.
        """
        LOG.info(
            'Start requesting on detach disks from vm and delete it from db.'
        )
        with self.uow:
            for disk in disks:
                try:
                    disk_data = self.uow.virtual_machines.get_disk_by_id(
                        disk.get('id')
                    )
                    self._detach_disk_from_vm(
                        str(disk_data.vm_id), DataSerializer.to_web(disk_data)
                    )
                    self.uow.virtual_machines.delete_disk(disk_data)
                except exceptions.UnexpectedDataArguments as err:
                    LOG.error(str(err))
            self.uow.commit()
        LOG.info('Disks were successfully detached and deleted from db.')

    def delete_vm(self, data: Dict) -> Optional[Dict]:
        """Delete a virtual machine by ID.

        Args:
            data (Dict): The data containing the ID of the virtual machine
                to delete.

        Returns:
            Dict: The serialized virtual machine data.

        Raises:
            VMStatusException: If the VM status is not valid for deletion.
            VMPowerStateException: If the VM power state is not valid
                for deletion.
        """
        LOG.info('Handling response on delete_vm.')
        vm_id = data.pop('vm_id', '')
        user_info = data.pop('user_info', {})

        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)

            available_statuses = [VmStatus.available.name, VmStatus.error.name]
            available_power_statuses = [VmPowerState.shut_off.name]
            try:
                self._check_vm_status(db_vm.status, available_statuses)
                self._check_vm_power_state(
                    db_vm.power_state, available_power_statuses
                )
                db_vm.status = VmStatus.deleting.name
                self.event_store.add_event(
                    str(db_vm.id),
                    user_info.get('id'),
                    self.delete_vm.__name__,
                    f'Set deleting status for VM {db_vm.name}.',
                )
                serialized_vm = DataSerializer.vm_to_web(db_vm)
                self.service_layer_rpc.cast(
                    self._delete_vm.__name__,
                    data_for_method={
                        'vm_id': serialized_vm.get('id', ''),
                        'token': user_info.get('token'),
                        'user_info': user_info,
                    },
                )
                LOG.info('Response on delete_vm was successfully processed.')
            except (
                exceptions.VMStatusException,
                exceptions.VMPowerStateException,
            ) as err:
                message = f'Handle error: {err!s} while deleting vm'
                LOG.error(message)
                db_vm.status = VmStatus.error.name
                db_vm.information = message
                raise
            else:
                return serialized_vm
            finally:
                self.uow.commit()

    def _delete_vm(self, data: Dict) -> None:
        """Delete a virtual machine from the database.

        Args:
            data (Dict): The data containing the ID of the virtual machine
                to delete.
        """
        LOG.info('Handling response on _delete_vm.')
        vm_id = data.pop('vm_id', '')
        user_info = data.pop('user_info', {})

        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            db_vm.status = VmStatus.detaching_disks.name
            self.uow.commit()
            try:
                for disk in db_vm.disks:
                    self._detach_disk_from_vm(
                        vm_id, DataSerializer.to_web(disk)
                    )
                self.uow.virtual_machines.delete(db_vm)
                self.event_store.add_event(
                    str(db_vm.id),
                    user_info.get('id'),
                    self._delete_vm.__name__,
                    f'VM {db_vm.name} was succesfully deleted.',
                )
                LOG.info('Response on _delete_vm was successfully processed.')
            except exceptions.UnexpectedDataArguments as err:
                message = f'Handle error: {err!s} while deleting vm.'
                LOG.error(message)
                db_vm.status = VmStatus.error.name
                db_vm.information = message
            finally:
                self.uow.commit()

    def start_vm(self, data: Dict) -> Dict:
        """Start a virtual machine by ID.

        This function changes the VM's status to starting and then
        sends a request to the service layer to start the VM.

        Args:
            data (Dict): The data containing the ID of the virtual machine
                to start.

        Returns:
            Dict: The serialized virtual machine data.
        """
        LOG.info('Handling response on start_vm.')
        vm_id = data.pop('vm_id', '')
        user_info = data.pop('user_info', {})
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            db_vm.status = VmStatus.starting.name
            self.uow.commit()
            self.event_store.add_event(
                str(db_vm.id),
                user_info.get('id'),
                self.start_vm.__name__,
                f'Set starting status for VM {db_vm.name}.',
            )
        serialized_vm = DataSerializer.vm_to_web(db_vm)
        serialized_vm['user_info'] = user_info
        self.service_layer_rpc.cast(
            self._start_vm.__name__, data_for_method=serialized_vm
        )
        LOG.info('Response on start_vm was successfully processed.')
        return serialized_vm

    def _start_vm(self, data: Dict) -> None:
        """Start a virtual machine and update the database with the new state.

        This function starts the VM using the domain layer and updates
        the database with the VM's new power state and status.

        Args:
            data (Dict): The data required to start the virtual machine.
        """
        LOG.info('Handling response on _start_vm.')
        alphabet = list(string.ascii_lowercase)
        user_info = data.pop('user_info', {})

        for i, disk in enumerate(data.get('disks', [])):
            if disk.get('type') == DiskType.volume.value:
                disk.update({'target': f'sd{alphabet[i]}'})
            else:
                disk.update({'target': f'sd{alphabet[i]}', 'emulation': 'ide'})
        with self.uow:
            db_vm = self.uow.virtual_machines.get(data.get('id', ''))
            try:
                start_info = self.domain_rpc.call(
                    BaseVMDriver.start.__name__, data_for_manager=data
                )
                db_vm.power_state = VmPowerState(
                    start_info.get('power_state')
                ).name
                db_vm.graphic_interface.url = (
                    f"{start_info.get('url', '') or ''}"
                    f":{start_info.get('port')}"
                )
                db_vm.status = VmStatus.available.name
                db_vm.information = ''
                self.uow.commit()
                self.event_store.add_event(
                    str(db_vm.id),
                    user_info.get('id'),
                    self._start_vm.__name__,
                    f'VM {db_vm.name} was successfully started.',
                )
                LOG.info('Response on _start_vm was successfully processed.')
            except (RpcCallException, RpcServerInitializedException) as err:
                message = f'Handle error: {err!s} while starting vm.'
                LOG.error(message)
                db_vm.status = VmStatus.error.name
                db_vm.information = message
            finally:
                self.uow.commit()

    def shut_off_vm(self, data: Dict) -> Dict:
        """Shut off a virtual machine by ID.

        This function changes the VM's status to shutting off and then
        sends a request to the service layer to shut off the VM.

        Args:
            data (Dict): The data containing the ID of the virtual machine
                to shut off.

        Returns:
            Dict: The serialized virtual machine data.
        """
        LOG.info('Handling response on shut_off_vm.')
        vm_id = data.pop('vm_id', '')
        user_info = data.pop('user_info', {})
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            self._check_vm_status(
                db_vm.status, [VmStatus.available.name, VmStatus.error.name]
            )
            self._check_vm_power_state(
                db_vm.power_state, [VmPowerState.running.name]
            )
            db_vm.status = VmStatus.shut_offing.name
            self.uow.commit()
            self.event_store.add_event(
                str(db_vm.id),
                user_info.get('id'),
                self.shut_off_vm.__name__,
                f'Set shut_off status for VM {db_vm.name}.',
            )
        serialized_vm = DataSerializer.vm_to_web(db_vm)
        serialized_vm['user_info'] = user_info
        self.service_layer_rpc.cast(
            self._shut_off_vm.__name__, data_for_method=serialized_vm
        )
        LOG.info('Response on shut_off_vm was successfully processed.')
        return serialized_vm

    def _shut_off_vm(self, data: Dict) -> None:
        """Shut off a virtual machine and update the database.

        This function calls the domain layer to shut off the VM and then
        updates the database with the VM's new power state and status.

        Args:
            data (Dict): The data required to shut off the virtual machine.
        """
        LOG.info('Handling response on _shut_off_vm.')
        user_info = data.pop('user_info', {})
        with self.uow:
            db_vm = self.uow.virtual_machines.get(data.get('id', ''))
            try:
                self.domain_rpc.call(
                    BaseVMDriver.turn_off.__name__, data_for_manager=data
                )
                db_vm.status = VmStatus.available.name
                db_vm.power_state = VmPowerState.shut_off.name
                db_vm.graphic_interface.url = ''
                self.event_store.add_event(
                    str(db_vm.id),
                    user_info.get('id'),
                    self._shut_off_vm.__name__,
                    f'VM {db_vm.name} was successfully shut off.',
                )
                LOG.info('Response on _shut_off_vm was successfully processed.')
            except (RpcCallException, RpcServerInitializedException) as err:
                message = f'Handle error: {err!s} while shutting off VM.'
                LOG.error(message)
                db_vm.status = VmStatus.error.name
                db_vm.information = message
            finally:
                self.uow.commit()

    @staticmethod
    def _prepare_vm_info_for_edit(vm_data: Dict) -> EditVmInfo:
        """Prepare the information needed to edit a virtual machine.

        Args:
            vm_data (Dict): A dictionary with all the parameters of the
                virtual machine.

        Returns:
            EditVmInfo: The prepared virtual machine information.
        """
        LOG.info(f'Preparing VM information for editing with data: {vm_data}')
        edit_vm_info = EditVmInfo(
            id=vm_data.pop('vm_id', ''),
            name=vm_data.pop('name', ''),
            description=vm_data.pop('description', ''),
            cpu=vm_data.pop('cpu', {}),
            ram=vm_data.pop('ram', {}),
            os=vm_data.pop('os', {}),
            graphic_interface=vm_data.pop('graphic_interface', {}),
            attach_volumes=[],
            attach_images=[],
            auto_create_volumes=[],
            detach_disks=[],
            edit_disks=[],
            new_virtual_interfaces=[],
            detach_virtual_interfaces=[],
            edit_virtual_interfaces=[],
        )
        LOG.info(f'Created edit_vm_info class: {edit_vm_info}')

        virtual_interfaces = vm_data.pop('virtual_interfaces', {})
        edit_vm_info.new_virtual_interfaces.extend(
            virtual_interfaces.get('new_virtual_interfaces', [])
        )
        edit_vm_info.detach_virtual_interfaces.extend(
            virtual_interfaces.get('detach_virtual_interfaces', [])
        )
        edit_vm_info.edit_virtual_interfaces.extend(
            virtual_interfaces.get('edit_virtual_interfaces', [])
        )

        disks = vm_data.pop('disks', {})
        for attach_disk in disks.pop('attach_disks', []):
            attach_disk.update({'qos': serialize_json(attach_disk.get('qos'))})
            if attach_disk.get('volume_id', ''):
                attach_disk.update(
                    {
                        'type': DiskType.volume.value,
                        'disk_id': attach_disk.get('volume_id', ''),
                        'read_only': attach_disk.get('read_only', False),
                    }
                )
                edit_vm_info.attach_volumes.append(attach_disk)
            elif attach_disk.get('image_id', ''):
                attach_disk.update(
                    {
                        'type': DiskType.image.value,
                        'disk_id': attach_disk.get('image_id', ''),
                        'read_only': True,
                    }
                )
                edit_vm_info.attach_images.append(attach_disk)
            elif attach_disk.get('storage_id', ''):
                edit_vm_info.auto_create_volumes.append(attach_disk)

        edit_vm_info.detach_disks.extend(disks.pop('detach_disks', []))
        edit_vm_info.edit_disks.extend(disks.pop('edit_disks', []))
        LOG.info('VM information was successfully prepared for editing.')
        return edit_vm_info

    def _update_db_vm_info(self, vm_id: str, edit_vm_info: EditVmInfo) -> None:
        """Update the database with the new VM information.

        Args:
            vm_id (str): The ID of the virtual machine to update.
            edit_vm_info (EditVmInfo): The new virtual machine information.
        """
        LOG.info('Updating VM information in database.')
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            db_vm.name = edit_vm_info.name
            db_vm.description = edit_vm_info.description
            for key, value in edit_vm_info.cpu.items():
                setattr(db_vm.cpu, key, value)
            for key, value in edit_vm_info.ram.items():
                setattr(db_vm.ram, key, value)
            for key, value in edit_vm_info.os.items():
                setattr(db_vm.os, key, value)
            for key, value in edit_vm_info.graphic_interface.items():
                setattr(db_vm.graphic_interface, key, value)
            self.uow.commit()
            LOG.info('VM was successfully updated in database.')

    def _edit_vm_disks(self, disks: List) -> None:
        """Update disks in the database.

        This function takes a list of dictionaries, each representing a disk,
        and updates the database with the new values.

        Args:
            disks (List): A list of dictionaries representing the disks to edit.
        """
        LOG.info('Bulk update disks in database.')
        self.uow.virtual_machines.bulk_update_disks(disks)
        self.uow.commit()
        LOG.info('Disks were successfully updated in database.')

    def _edit_virtual_interfaces(self, virtual_interfaces: List) -> None:
        """Update virtual interfaces in the database.

        Args:
            virtual_interfaces (List): A list of dictionaries representing
                the virtual interfaces to edit.
        """
        LOG.info('Bulk update virtual interfaces in database.')
        self.uow.virtual_machines.bulk_update_virtual_interfaces(
            virtual_interfaces
        )
        self.uow.commit()
        LOG.info('Virtual interfaces were successfully updated in database.')

    def _detach_virtual_interfaces_from_vm(self, virt_interfaces: List) -> None:
        """Detach virtual interfaces from a virtual machine.

        Args:
            virt_interfaces (List): A list of virtual interfaces to detach.
        """
        LOG.info('Bulk detaching virtual interfaces from database.')
        self.uow.virtual_machines.delete_virtual_interfaces(virt_interfaces)
        self.uow.commit()
        LOG.info('Virtual interfaces were successfully detached from database.')

    def _add_virtual_interfaces_to_vm(
        self, vm_id: str, virt_interfaces: List
    ) -> None:
        """Add virtual interfaces to a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine to add the interfaces to.
            virt_interfaces (List): A list of virtual interfaces to add.
        """
        LOG.info('Adding virtual interfaces into database for VM.')
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            for virt_interface in virt_interfaces:
                db_vm.virtual_interfaces.append(
                    cast(
                        orm.VirtualInterface,
                        DataSerializer.to_db(
                            virt_interface, orm.VirtualInterface
                        ),
                    )
                )
            self.uow.commit()
        LOG.info(
            'Virtual interfaces were successfully added into database for VM.'
        )

    def edit_vm(self, edit_info: Dict) -> Dict:
        """Edit a virtual machine by ID.

        This function checks if the VM is in the right state to be edited,
        changes the VM's status to editing, and then calls the appropriate
        function to handle the editing process.

        Args:
            edit_info (Dict): The data containing the information to edit the
                VM.

        Returns:
            Dict: The serialized virtual machine data.
        """
        LOG.info('Handling response on edit VM.')
        user_info = edit_info.pop('user_info', {})
        with self.uow:
            db_vm = self.uow.virtual_machines.get(edit_info.get('vm_id', ''))
            serialized_vm = DataSerializer.vm_to_web(db_vm)
            available_states = [VmStatus.available.name, VmStatus.error.name]
            available_power_states = [
                VmPowerState.shut_off.name,
                VmPowerState.running.name,
            ]
            try:
                self._check_vm_status(db_vm.status, available_states)
                self._check_vm_power_state(
                    db_vm.power_state, available_power_states
                )
                db_vm.status = VmStatus.editing.name
                self.uow.commit()
                if db_vm.power_state == VmPowerState.shut_off.name:
                    self.service_layer_rpc.cast(
                        self._edit_shut_offed_vm.__name__,
                        data_for_method={
                            'edit_info': edit_info,
                            'user_info': user_info,
                        },
                    )
            except (
                exceptions.VMStatusException,
                exceptions.VMPowerStateException,
            ) as err:
                message = f'Handle error: {err!s} while editing VM.'
                LOG.error(message)
                db_vm.information = message
        LOG.info('Response on edit VM was successfully processed.')
        return serialized_vm

    def _edit_shut_offed_vm(self, data: Dict) -> None:
        """Edit a shut-off virtual machine.

        This function handles the editing process for VMs that are in
        a shut-off state.

        Args:
            data (Dict): The data containing the information to edit the VM.
        """
        LOG.info(f'Handling response on _edit_vm with data: {data}')
        data.pop('user_info', {})
        vm_edit_info = self._prepare_vm_info_for_edit(data.pop('edit_info', {}))
        self._update_db_vm_info(vm_edit_info.id, vm_edit_info)

        self._process_vm_edit_disks(vm_edit_info)
        self._process_vm_edit_interfaces(vm_edit_info)

        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_edit_info.id)
            db_vm.status = VmStatus.available.name
            db_vm.information = ''
            self.uow.commit()
            self._process_vm_volumes(vm_edit_info, db_vm)
        LOG.info('Response on _edit_vm was successfully processed.')

    def _process_vm_edit_disks(self, vm_edit_info: EditVmInfo) -> None:
        """Process editing and detaching disks for the VM."""
        if vm_edit_info.edit_disks:
            self._edit_vm_disks(vm_edit_info.edit_disks)

        if vm_edit_info.detach_disks:
            self._detach_disks_from_vm(vm_edit_info.detach_disks)

    def _process_vm_edit_interfaces(self, vm_edit_info: EditVmInfo) -> None:
        """Process editing and detaching virtual interfaces for the VM."""
        with self.uow:
            if vm_edit_info.edit_virtual_interfaces:
                self._edit_virtual_interfaces(
                    vm_edit_info.edit_virtual_interfaces
                )

            if vm_edit_info.detach_virtual_interfaces:
                self._detach_virtual_interfaces_from_vm(
                    vm_edit_info.detach_virtual_interfaces
                )
            if vm_edit_info.new_virtual_interfaces:
                self._add_virtual_interfaces_to_vm(
                    vm_edit_info.id, vm_edit_info.new_virtual_interfaces
                )

    def _process_vm_volumes(
        self,
        vm_edit_info: EditVmInfo,
        db_vm: orm.VirtualMachines,
    ) -> None:
        """Process attaching volumes and creating new disks for the VM."""
        if vm_edit_info.auto_create_volumes:
            created_disks = self._create_volumes(
                db_vm.name, vm_edit_info.auto_create_volumes
            )
            vm_edit_info.attach_volumes.extend(created_disks)

        if vm_edit_info.attach_volumes or vm_edit_info.attach_images:
            self._add_disks_to_vm(
                vm_edit_info.id,
                vm_edit_info.attach_volumes + vm_edit_info.attach_images,
            )

    def vnc(self, data: Dict) -> Dict:
        """Access the VNC session of a virtual machine.

        Args:
            data (Dict): The data containing the ID of the virtual machine.

        Returns:
            Dict: The VNC session information.

        Raises:
            RpcCallException: If an error occurs during the RPC call.
            RpcServerInitializedException: If the RPC server is not initialized.
        """
        vm_id = data.pop('vm_id', '')
        data.pop('user_info', '')
        with self.uow:
            db_vm = self.uow.virtual_machines.get(vm_id)
            serialized_vm = DataSerializer.vm_to_web(db_vm)
            try:
                result: Dict = self.domain_rpc.call(
                    BaseVMDriver.vnc.__name__, data_for_manager=serialized_vm
                )
            except (RpcCallException, RpcServerInitializedException) as err:
                message = f'Handle error: {err!s} while accessing VNC.'
                LOG.error(message)
                raise
            else:
                return result

    @periodic_task(interval=10)
    def monitoring(self) -> None:
        """Monitor the state of virtual machines periodically.

        This task checks the state of VMs and updates their power state
        and status in the database.

        This method runs as a periodic task every 10 seconds.
        """
        LOG.info('Start monitoring.')
        virsh_list = get_vms_state()
        with self.uow:
            with synchronized_session(self.uow.session):
                for db_vm in self.uow.virtual_machines.get_all():
                    db_vm_power_state = virsh_list.get(db_vm.name, '')
                    if not db_vm_power_state:
                        db_vm.power_state = VmPowerState.shut_off.name
                    elif db_vm_power_state == VmPowerState.running.name:
                        db_vm.power_state = VmPowerState[db_vm_power_state].name
                        db_vm.status = VmStatus.available.name
                        db_vm.information = ''
                    else:
                        db_vm.power_state = VmPowerState[db_vm_power_state].name
            self.uow.commit()
        LOG.info('Stop monitoring.')
