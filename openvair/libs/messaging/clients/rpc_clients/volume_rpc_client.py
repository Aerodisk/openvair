"""Proxy implementation for the Volume Service Layer.

This module defines the `VolumeServiceLayerRPCClient` class, which serves as a
proxy for interacting with the Volume Service Layer. The proxy class
encapsulates the details of the RPC communication with the service layer,
providing a consistent and easy-to-use interface for external code.

The `VolumeServiceLayerRPCClient` class implements the
`VolumeServiceLayerProtocolInterface`, which defines the contract for
interacting with the volume service layer. This allows the external code
to work with the proxy class without needing to know the underlying
implementation details.

Classes:
    VolumeServiceLayerRPCClient: Proxy implementation for the Volume Service
        Layer, providing a consistent interface for interacting with the
        volume service.
"""

from typing import Dict, List

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.volume import (
    VolumeServiceLayerProtocolInterface,
)


class VolumeServiceLayerRPCClient(VolumeServiceLayerProtocolInterface):
    """Proxy implementation for VolumeServiceLayerProtocolInterface

    This class provides methods to interact with the Volume Service Layer
    through RPC calls.

    Attributes:
        volume_service_rpc (RabbitRPCClient): RPC client for communicating with
            the Volume Service Layer.
    """

    def __init__(self) -> None:
        """Initialize the VolumeServiceLayerRPCClient.

        This method sets up the necessary components for the
        VolumeServiceLayerRPCClient, including the RabbitMQ RPC client for
        communicating with the Volume Service Layer.
        """
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.Volume.SERVICE_LAYER
        )

    def get_volume(self, data: Dict) -> Dict:
        """Retrieve a volume by its ID.

        Args:
            data (Dict): Data containing the volume ID.

        Returns:
            Dict: Serialized volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.get_volume.__name__,
            data_for_method=data,
        )
        return result

    def get_all_volumes(self, data: Dict) -> List[Dict]:
        """Retrieve all volumes from the database.

        Args:
            data (Dict): Data for filtering volumes.

        Returns:
            List[Dict]: List of serialized volume data.
        """
        result: List[Dict] = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.get_all_volumes.__name__,
            data_for_method=data,
        )
        return result

    def create_volume(self, volume_info: Dict) -> Dict:
        """Create a new volume.

        Args:
            volume_info (Dict): Information about the volume to be created.

        Returns:
            Dict: Serialized volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.create_volume.__name__,
            data_for_method=volume_info,
        )
        return result

    def clone_volume(self, data: Dict) -> Dict:
        """Clone an existing volume.

        Args:
            data (Dict): Data containing the source volume information.

        Returns:
            Dict: Serialized cloned volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.clone_volume.__name__,
            data_for_method=data,
        )
        return result

    def create_from_template(self, data: Dict) -> Dict:
        """Create a new volume from a template.

        Args:
            data (Dict): Data containing the template ID and volume details.

        Returns:
            Dict: Serialized volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.create_from_template.__name__,
            data_for_method=data,
        )
        return result

    def extend_volume(self, data: Dict) -> Dict:
        """Extend the size of an existing volume.

        Args:
            data (Dict): Data containing the volume ID and new size.

        Returns:
            Dict: Serialized volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.extend_volume.__name__,
            data_for_method=data,
        )
        return result

    def delete_volume(self, data: Dict) -> Dict:
        """Delete an existing volume.

        Args:
            data (Dict): Data containing the volume ID.

        Returns:
            Dict: Serialized volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.delete_volume.__name__,
            data_for_method=data,
        )
        return result

    def edit_volume(self, data: Dict) -> Dict:
        """Edit the details of an existing volume.

        Args:
            data (Dict): Data containing the volume ID and new details.

        Returns:
            Dict: Serialized volume data.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.edit_volume.__name__,
            data_for_method=data,
        )
        return result

    def attach_volume(self, data: Dict) -> Dict:
        """Attach a volume to a virtual machine.

        Args:
            data (Dict): Data containing the volume ID and VM details.

        Returns:
            Dict: Result of the attach operation.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.attach_volume.__name__,
            data_for_method=data,
        )
        return result

    def detach_volume(self, data: Dict) -> Dict:
        """Detach a volume from a virtual machine.

        Args:
            data (Dict): Data containing the volume ID and VM details.

        Returns:
            Dict: Result of the detach operation.
        """
        result: Dict = self.service_rpc_client.call(
            VolumeServiceLayerProtocolInterface.detach_volume.__name__,
            data_for_method=data,
        )
        return result
