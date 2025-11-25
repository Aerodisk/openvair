"""Proxy implementation for the VM Service Layer.

This module defines the `VMServiceLayerRPCClient` class, which serves as a
proxy for interacting with the VM Service Layer. The proxy class
encapsulates the details of the RPC communication with the service layer,
providing a consistent and easy-to-use interface for external code.

The `VMServiceLayerRPCClient` class implements the
`VMServiceLayerProtocolInterface`, which defines the contract for
interacting with the VM service layer. This allows the external code
to work with the proxy class without needing to know the underlying
implementation details.

Classes:
    VMServiceLayerRPCClient: Proxy implementation for the VM Service
        Layer, providing a consistent interface for interacting with the
        VM service.
"""

from typing import Dict, List

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.vm import (
    VMServiceLayerProtocolInterface,
)


class VMServiceLayerRPCClient(VMServiceLayerProtocolInterface):
    """Proxy implementation for VMServiceLayerProtocolInterface

    This class provides methods to interact with the VM Service Layer
    through RPC calls.

    Attributes:
        vm_service_rpc (RabbitRPCClient): RPC client for communicating with
            the VM Service Layer.
    """

    def __init__(self) -> None:
        """Initialize the VMServiceLayerRPCClient.

        This method sets up the necessary components for the
        VMServiceLayerRPCClient, including the RabbitMQ RPC client for
        communicating with the VM Service Layer.
        """
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.VMS.SERVICE_LAYER
        )

    def get_vm(self, data: Dict) -> Dict:
        """Retrieve a VM by its ID.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.get_vm.__name__,
            data_for_method=data,
        )
        return result

    def get_all_vms(self) -> List[Dict]:
        """Retrieve all VMs from the database.

        Returns:
            List[Dict]: List of serialized VM data.
        """
        result: List[Dict] = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.get_all_vms.__name__,
            data_for_method={},
        )
        return result

    def create_vm(self, data: Dict) -> Dict:
        """Create a new VM.

        Args:
            data (Dict): Information about the VM to be created.

        Returns:
            Dict: Serialized VM data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.create_vm.__name__,
            data_for_method=data,
        )
        return result

    def delete_vm(self, data: Dict) -> Dict:
        """Delete an existing VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.delete_vm.__name__,
            data_for_method=data,
        )
        return result

    def start_vm(self, data: Dict) -> Dict:
        """Start a VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.start_vm.__name__,
            data_for_method=data,
        )
        return result

    def shut_off_vm(self, data: Dict) -> Dict:
        """Shut off a VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.shut_off_vm.__name__,
            data_for_method=data,
        )
        return result

    def edit_vm(self, edit_info: Dict) -> Dict:
        """Edit an existing VM.

        Args:
            edit_info (Dict): Information about the VM to be edited.

        Returns:
            Dict: Serialized VM data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.edit_vm.__name__,
            data_for_method=edit_info,
        )
        return result

    def vnc(self, data: Dict) -> Dict:
        """Retrieve VNC information for a VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: VNC connection data.
        """
        result: Dict = self.service_rpc_client.call(
            VMServiceLayerProtocolInterface.vnc.__name__,
            data_for_method=data,
        )
        return result
