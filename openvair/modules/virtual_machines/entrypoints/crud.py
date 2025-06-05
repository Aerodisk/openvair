"""Module for virtual machine CRUD operations.

This module provides a class `VMCrud` that contains methods for performing
CRUD (Create, Read, Update, Delete) operations on virtual machines.
The operations are executed by calling the service layer via RPC.

Classes:
    VMCrud: Provides methods to create, retrieve, update, and delete
        virtual machines by interacting with the service layer.
"""

from typing import Dict, List

from openvair.libs.log import get_logger
from openvair.libs.validation.validators import Validator
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.virtual_machines.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
)
from openvair.modules.virtual_machines.entrypoints import schemas
from openvair.modules.virtual_machines.service_layer import services

LOG = get_logger(__name__)


class VMCrud:
    """Class for virtual machine CRUD operations.

    This class provides methods to interact with the service layer to
    perform CRUD operations on virtual machines.

    Attributes:
        service_layer_rpc (Protocol): An RPC client for communicating with
            the service layer.
    """

    def __init__(self) -> None:
        """Initialize VMCrud with an RPC client."""
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_vm(self, vm_id: str) -> Dict:
        """Retrieve a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to retrieve.

        Returns:
            Dict: The virtual machine data.
        """
        LOG.info('Call service layer to get VM by ID: %s.', vm_id)
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.get_vm.__name__,
            data_for_method={'vm_id': vm_id},
        )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def get_all_vms(self) -> List:
        """Retrieve all virtual machines.

        Returns:
            Page: A paginated list of all virtual machines.
        """
        LOG.info('Call service layer to get all VMs.')
        result = self.service_layer_rpc.call(
            services.VMServiceLayerManager.get_all_vms.__name__,
            data_for_method={},
        )
        LOG.debug('Response from service layer: %s.', result)
        return Validator.validate_objects(result, schemas.VirtualMachineInfo)

    def create_vm(self, data: Dict, user_info: Dict) -> Dict:
        """Create a new virtual machine.

        Args:
            data (Dict): The data required to create a virtual machine.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The created virtual machine data.
        """
        LOG.info('Call service layer to create VM with data: %s.', data)
        data.update({'user_info': user_info})
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.create_vm.__name__,
            data_for_method=data,
        )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def delete_vm(self, vm_id: str, user_info: Dict) -> Dict:
        """Delete a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to delete.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The result of the deletion operation.
        """
        LOG.info('Call service layer to delete VM by ID: %s.', vm_id)
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.delete_vm.__name__,
            data_for_method={'vm_id': vm_id, 'user_info': user_info},
        )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def start_vm(self, vm_id: str, user_info: Dict) -> Dict:
        """Start a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to start.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The result of the start operation.
        """
        LOG.info('Call service layer to start VM by ID: %s.', vm_id)
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.start_vm.__name__,
            data_for_method={'vm_id': vm_id, 'user_info': user_info},
        )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def shut_off_vm(self, vm_id: str, user_info: Dict) -> Dict:
        """Shut off a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to shut off.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The result of the shut-off operation.
        """
        LOG.info('Call service layer to shut off VM by ID: %s.', vm_id)
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.shut_off_vm.__name__,
            data_for_method={'vm_id': vm_id, 'user_info': user_info},
        )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def edit_vm(self, vm_id: str, data: Dict, user_info: Dict) -> Dict:
        """Edit a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to edit.
            data (Dict): The data to update the virtual machine.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The updated virtual machine data.
        """
        LOG.info('Call service layer to edit VM by ID: %s.', vm_id)
        data.update({'vm_id': vm_id, 'user_info': user_info})
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.edit_vm.__name__,
            data_for_method=data,
        )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def vnc(self, vm_id: str, user_info: Dict) -> Dict:
        """Access the VNC session of a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The VNC session details.
        """
        result: Dict = self.service_layer_rpc.call(
            services.VMServiceLayerManager.vnc.__name__,
            data_for_method={'vm_id': vm_id, 'user_info': user_info},
        )
        return result

    def get_snapshots(self, vm_id: str, _user_info: Dict) -> List:
        """Retrieve all snapshots of a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.
            user_info (Dict): The user information for authorization.

        Returns:
            List: A list of all snapshots of the specific virtual machine.
        """
        LOG.info(f'Call service layer to get snapshots of VM with ID: {vm_id}')

        # TODO: Заменить на вызов RPC
        import uuid
        snapshot_id = str(uuid.uuid4())

        result = [
            {
                'vm_id': vm_id,
                'id': snapshot_id,
                'name': 'NAME1',
                'parent': 'ROOT',
                'status': 'active',
                'description': 'DESCRIPTION1',
            },
            {
                'vm_id': vm_id,
                'id': snapshot_id,
                'name': 'NAME2',
                'parent': None,
                'status': 'active',
                'description': None,
            }
        ]
        # result: Dict = self.service_layer_rpc.call(
        #     services.VMServiceLayerManager.get_snapshots.__name__,
        #     data_for_method={'vm_id': vm_id, 'user_info': user_info},
        # )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def get_snapshot(
            self, vm_id: str, snap_id: str, _user_info: Dict
    ) -> Dict:
        """Retrieve a snapshot of a specific virtual machine by snapshot ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            snap_id (str): The ID of the snapshot.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The snapshot data.
        """
        LOG.info(f'Call service layer to get snapshot of VM (ID: {vm_id}) '
                 f'by snapshot ID: {snap_id}.')

        # TODO: Заменить на вызов RPC
        result = {
            'vm_id': vm_id,
            'id': snap_id,
            'name': 'NAME',
            'parent': 'ROOT',
            'status': 'active',
            'description': 'DESCRIPTION',
        }
        # result: Dict = self.service_layer_rpc.call(
        #     services.VMServiceLayerManager.get_snapshot.__name__,
        #     data_for_method={
        #         'vm_id': vm_id,
        #         'snap_id': snap_id,
        #         'user_info': user_info
        #     },
        # )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def create_snapshot(
            self, vm_id: str, data: Dict, user_info: Dict
    ) -> Dict:
        """Create a new snapshot of the virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine where snapshot will be
            created.
            data (Dict): The data required to create a new snapshot of the
            virtual machine.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The created snapshot data matching SnapshotInfo schema.
        """
        LOG.info(f'Call service layer to create snapshot of VM (ID: {vm_id}) '
                 f'with data: {data}')

        data.update({'vm_id': str(vm_id), 'user_info': user_info})
        # TODO: Заменить на вызов RPC
        import uuid
        snapshot_id = str(uuid.uuid4())
        result = {
            "vm_id": vm_id,
            "id": snapshot_id,
            "vm_name": "vm_name",
            "name": "snap_name",
            "parent": "parent_name",
            "description": "Open vAIR"
        }
        # result: Dict = self.service_layer_rpc.call(
        #     services.VMServiceLayerManager.create_snapshot.__name__,
        #     data_for_method=data,
        # )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def revert_snapshot(
            self, vm_id: str, snap_id: str, _user_info: Dict
    ) -> Dict:
        """Revert a virtual machine to a snapshot.

        Args:
            vm_id (str): The ID of the virtual machine where the snapshot
            will be reverted.
            snap_id (str): The ID of the snapshot to revert.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The reverted snapshot data matching SnapshotInfo schema.
        """
        LOG.info(f'Call service layer to revert snapshot of VM (ID: {vm_id}) '
                 f'with snapshot ID: {snap_id}')

        # TODO: Заменить на вызов RPC
        result = {
            'vm_id': vm_id,
            'id': snap_id,
            'name': 'NAME',
            'parent': 'ROOT',
            'status': 'active',
            'description': 'DESCRIPTION'
        }
        # result: Dict = self.service_layer_rpc.call(
        #     services.VMServiceLayerManager.revert_snapshot.__name__,
        #     data_for_method={
        #         'vm_id': vm_id,
        #         'snap_id': snap_id,
        #         'user_info': user_info
        #     },
        # )
        LOG.debug('Response from service layer: %s.', result)
        return result

    def delete_snapshot(
            self, vm_id: str, snap_id: str, _user_info: Dict
    ) -> Dict:
        """Delete a snapshot of virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine where the snapshot
            will be deleted.
            snap_id (str): The ID of the snapshot to delete.
            user_info (Dict): The user information for authorization.

        Returns:
            Dict: The deleted snapshot data matching SnapshotInfo schema.
        """
        LOG.info(f'Call service layer to delete snapshot of VM (ID: {vm_id}) '
                 f'with snapshot ID: {snap_id}')

        # TODO: Заменить на вызов RPC
        result = {
            'status': 'SUCCESS'
        }
        # result: Dict = self.service_layer_rpc.call(
        #     services.VMServiceLayerManager.delete_snapshot.__name__,
        #     data_for_method={
        #         'vm_id': vm_id, 'snap_id': snap_id, 'user_info': user_info
        #     },
        # )
        LOG.debug('Response from service layer: %s.', result)
        return result
