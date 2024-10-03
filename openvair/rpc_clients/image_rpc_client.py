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

from typing import TYPE_CHECKING, Dict, List

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.protocol import Protocol as MessagingProtocol
from openvair.interfaces.image_service_interface import (
    ImageServiceLayerProtocolInterface,
)

if TYPE_CHECKING:
    from openvair.libs.messaging.rpc import RabbitRPCClient


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
        self.service_rpc_client: RabbitRPCClient = MessagingProtocol(
            client=True
        )(RPCQueueNames.Image.SERVICE_LAYER)

    def get_image(self, data: Dict) -> Dict:
        """Retrieve an image by its ID.

        Args:
            data (Dict): Data containing the image ID.

        Returns:
            Dict: Serialized image data.
        """
        return self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.get_image.__name__,
            data_for_method=data,
        )

    def get_all_images(self, data: Dict) -> List[Dict]:
        """Retrieve all images from the database.

        Args:
            data (Dict): Data for filtering images.

        Returns:
            List[Dict]: List of serialized image data.
        """
        return self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.get_all_images.__name__,
            data_for_method=data,
        )

    def upload_image(self, image_info: Dict) -> Dict:
        """Upload a new image.

        Args:
            image_info (Dict): Information about the image to be uploaded.

        Returns:
            Dict: Serialized image data.
        """
        return self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.upload_image.__name__,
            data_for_method=image_info,
        )

    def delete_image(self, data: Dict) -> None:
        """Delete an existing image.

        Args:
            data (Dict): Data containing the image ID.

        Returns:
            None
        """
        return self.service_rpc_client.call(
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
        return self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.attach_image.__name__,
            data_for_method=data,
        )

    def detach_image(self, data: Dict) -> Dict:
        """Detach an image from a virtual machine.

        Args:
            data (Dict): Data containing the image ID and VM details.

        Returns:
            Dict: Result of the detach operation.
        """
        return self.service_rpc_client.call(
            ImageServiceLayerProtocolInterface.detach_image.__name__,
            data_for_method=data,
        )
