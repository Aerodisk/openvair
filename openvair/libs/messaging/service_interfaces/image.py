"""Module for managing image-related operations in the service layer.

This module provides functionality for handling image operations such as
uploading, retrieving, and managing image metadata. It serves as an
intermediary between the API layer and the domain layer, coordinating
image-related tasks and managing database interactions.

The module includes an interface definition for the image service layer manager,
which outlines the methods that should be implemented by any class responsible
for handling image operations.

Classes:
    ImageServiceLayerProtocolInterface: Interface for handling image service
        layer operations.
"""

from typing import Dict, List, Protocol


class ImageServiceLayerProtocolInterface(Protocol):
    """Interface for the ImageServiceLayerManager.

    This interface defines the methods that should be implemented by any class
    that manages image-related operations in the service layer.
    """

    def get_image(self, data: Dict) -> Dict:
        """Retrieve an image by its ID.

        Args:
            data (Dict): Data containing the image ID.

        Returns:
            Dict: Serialized image data.
        """
        ...

    def get_all_images(self, data: Dict) -> List[Dict]:
        """Retrieve all images from the database.

        Args:
            data (Dict): Data for filtering images.

        Returns:
            List[Dict]: List of serialized image data.
        """
        ...

    def upload_image(self, image_info: Dict) -> Dict:
        """Upload a new image.

        Args:
            image_info (Dict): Information about the image to be uploaded.

        Returns:
            Dict: Serialized image data.
        """
        ...

    def delete_image(self, data: Dict) -> None:
        """Delete an existing image.

        Args:
            data (Dict): Data containing the image ID.

        Returns:
            None
        """
        ...

    def attach_image(self, data: Dict) -> Dict:
        """Attach an image to a virtual machine.

        Args:
            data (Dict): Data containing the image ID and VM details.

        Returns:
            Dict: Result of the attach operation.
        """
        ...

    def detach_image(self, data: Dict) -> Dict:
        """Detach an image from a virtual machine.

        Args:
            data (Dict): Data containing the image ID and VM details.

        Returns:
            Dict: Result of the detach operation.
        """
        ...
