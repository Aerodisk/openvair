"""Proxy implementation for the Image Service Layer.

This module defines the `ImageServiceLayerRPCClient` class, which serves as a
proxy for interacting with the Image Service Layer. The proxy class
encapsulates the details of the RPC communication with the service layer,
providing a consistent and easy-to-use interface for external code.

The `ImageServiceLayerRPCClient` class implements the
`ImageServiceLayerProtocolInterface`, which defines the contract for
interacting with the image service layer. This allows the external code
to work with the proxy class without needing to know the underlying
implementation details.

Classes:
    ImageServiceLayerRPCClient: Proxy implementation for the Image Service
        Layer, providing a consistent interface for interacting with the
        image service.
"""

from typing import Dict, List

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.image import (
    ImageServiceLayerProtocolInterface,
)


class ImageServiceLayerRPCClient(ImageServiceLayerProtocolInterface):
    """Proxy implementation for ImageServiceLayerProtocolInterface

    This class provides methods to interact with the Image Service Layer
    through RPC calls.

    Attributes:
        image_service_rpc (RabbitRPCClient): RPC client for communicating with
            the Image Service Layer.
    """

    def __init__(self) -> None:
        """Initialize the ImageServiceLayerRPCClient.

        This method sets up the necessary components for the
        ImageServiceLayerRPCClient, including the RabbitMQ RPC client for
        communicating with the Image Service Layer.
        """
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.Image.SERVICE_LAYER
        )

    def get_image(self, data: Dict) -> Dict:
        """Retrieve an image by its ID.

        Args:
            data (Dict): Data containing the image ID.

        Returns:
            Dict: Serialized image data.
        """
        result: Dict = self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.get_image.__name__,
            data_for_method=data,
        )
        return result

    def get_all_images(self, data: Dict) -> List[Dict]:
        """Retrieve all images from the database.

        Args:
            data (Dict): Data for filtering images.

        Returns:
            List[Dict]: List of serialized image data.
        """
        result: List[Dict] = self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.get_all_images.__name__,
            data_for_method=data,
        )
        return result

    def upload_image(self, image_info: Dict) -> Dict:
        """Upload a new image.

        Args:
            image_info (Dict): Information about the image to be uploaded.

        Returns:
            Dict: Serialized image data.
        """
        result: Dict = self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.upload_image.__name__,
            data_for_method=image_info,
        )
        return result

    def delete_image(self, data: Dict) -> None:
        """Delete an existing image.

        Args:
            data (Dict): Data containing the image ID.

        Returns:
            None
        """
        self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.delete_image.__name__,
            data_for_method=data,
        )

    def attach_image(self, data: Dict) -> Dict:
        """Attach an image to a virtual machine.

        Args:
            data (Dict): Data containing the image ID and VM details.

        Returns:
            Dict: Result of the attach operation.
        """
        result: Dict = self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.attach_image.__name__,
            data_for_method=data,
        )
        return result

    def detach_image(self, data: Dict) -> Dict:
        """Detach an image from a virtual machine.

        Args:
            data (Dict): Data containing the image ID and VM details.

        Returns:
            Dict: Result of the detach operation.
        """
        result: Dict = self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.detach_image.__name__,
            data_for_method=data,
        )
        return result
