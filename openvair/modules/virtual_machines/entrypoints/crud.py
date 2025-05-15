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

    def clone_vm(self, vm_id: str, count: int, user_info: Dict) -> List[Dict]:
        """Clone a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine to copy.
            count (int): The number of copies to create.
            user_info (Dict): The user information for authorization.

        Returns:
            List[Dict]: The list of cloned virtual machine data.
        """
        LOG.info(
            f'Call service layer to clone VM by ID: {vm_id} {count} times.'
        )
        result: List[Dict] = self.service_layer_rpc.call(
            services.VMServiceLayerManager.clone_vm.__name__,
            data_for_method={
                'vm_id': vm_id,
                'count': count,
                'user_info': user_info
            },
        )
        LOG.debug(f'Response from service layer: {result}')
        return result
