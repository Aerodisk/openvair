"""CRUD module for managing image operations.

This module defines the `ImageCrud` class, which serves as an intermediary
between the API layer and the service layer. It provides methods for
performing CRUD operations on images, such as retrieving, uploading,
deleting, and attaching or detaching images from virtual machines.

Classes:
    ImageCrud: Class for handling image-related CRUD operations.
"""

from typing import Dict, List, Optional, cast

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import validate_objects
from openvair.modules.image.config import (
    PERMITTED_EXTENSIONS,
    API_SERVICE_LAYER_QUEUE_NAME,
)
from openvair.modules.image.entrypoints import schemas
from openvair.modules.image.service_layer import services
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.image.entrypoints.exceptions import (
    NotSupportedExtensionError,
)

LOG = get_logger(__name__)


class ImageCrud:
    """Class for handling CRUD operations related to images.

    This class communicates with the service layer using an RPC-based
    messaging client. It provides methods for interacting with images,
    including retrieving metadata, uploading new images, deleting images,
    and managing image attachments to virtual machines.

    Attributes:
        service_layer_rpc (MessagingClient): Messaging client for sending
        requests to the service layer.
    """

    def __init__(self) -> None:
        """Initialize the ImageCrud instance.

        Sets up the messaging client for communication with the service layer.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    @staticmethod
    def _check_image_extension(image_name: str) -> None:
        """Validate the file extension of the image.

        Checks whether the provided image file has a supported extension.

        Args:
            image_name (str): Name of the image file to validate.

        Raises:
            NotSupportedExtensionError: If the image file extension is not
                supported.
        """
        if ext := image_name.split('.')[-1] not in PERMITTED_EXTENSIONS:
            message = (
                'Incorrect extension of uploading image, '
                f'{ext} is not supported.'
            )
            LOG.error(message)
            raise NotSupportedExtensionError(message)

    def get_image(self, image_id: str) -> Dict:
        """Retrieve metadata of a specific image by its ID.

        This method sends a request to the service layer to fetch metadata
        for the image with the specified ID.

        Args:
            image_id (str): ID of the image to retrieve.

        Returns:
            Dict: Metadata of the specified image.
        """
        LOG.info('Call service layer on get image.')
        result: Dict = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.get_image.__name__,
            data_for_method={'image_id': image_id},
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def get_all_images(self, storage_id: Optional[str]) -> List:
        """Retrieve a list of all images, optionally filtered by storage ID.

        This method sends a request to the service layer to fetch a list
        of images. It validates the returned objects using the `schemas.Image`.

        Args:
            storage_id (Optional[str]): ID of the storage to filter images by.

        Returns:
            List: A list of validated image metadata.
        """
        LOG.info('Call service layer on get all images.')
        result: List = cast(
            List,
            self.service_layer_rpc.call(
                services.ImageServiceLayerManager.get_all_images.__name__,
                data_for_method={'storage_id': storage_id},
            ),
        )
        LOG.debug('Response from service layer: %s.' % result)
        return validate_objects(result, schemas.Image)

    def upload_image(
        self,
        name: str,
        storage_id: str,
        description: str,
        user_info: Dict,
    ) -> Dict:
        """Upload a new image to the storage.

        This method validates the file extension, then sends a request to the
        service layer to upload the image to the specified storage.

        Args:
            name (str): Name of the image file.
            storage_id (str): ID of the storage where the image will be
                uploaded.
            description (str): Description of the image.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: Metadata of the uploaded image.

        Raises:
            NotSupportedExtensionError: If the image file extension is not
                supported.
        """
        LOG.info('Call service layer on upload image.')
        self._check_image_extension(image_name=name)
        result: Dict = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.upload_image.__name__,
            data_for_method={
                'name': name,
                'storage_id': storage_id,
                'description': description,
                'user_info': user_info,
            },
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def delete_image(
        self,
        image_id: str,
        user_info: Dict,
    ) -> Dict:
        """Delete an image by its ID.

        This method sends a request to the service layer to delete the image
        with the specified ID.

        Args:
            image_id (str): ID of the image to delete.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: Response from the service layer indicating the result of the
                deletion.
        """
        LOG.info('Call service layer on delete image.')
        result: Dict = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.delete_image.__name__,
            data_for_method={'image_id': image_id, 'user_info': user_info},
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def attach_image(
        self,
        image_id: str,
        data: Dict,
        user_info: Dict,
    ) -> Dict:
        """Attach an image to a virtual machine.

        This method sends a request to the service layer to attach the image
        with the specified ID to a virtual machine.

        Args:
            image_id (str): ID of the image to attach.
            data (Dict): Data containing the virtual machine ID.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: Response from the service layer indicating the result of the
                attachment.
        """
        data.update({'image_id': image_id, 'user_info': user_info})
        LOG.info('Call service layer on attach image.')
        result: Dict = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.attach_image.__name__,
            data_for_method=data,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def detach_image(
        self,
        image_id: str,
        detach_info: Dict,
        user_info: Dict,
    ) -> Dict:
        """Detach an image from a virtual machine.

        This method sends a request to the service layer to detach the image
        with the specified ID from a virtual machine.

        Args:
            image_id (str): ID of the image to detach.
            detach_info (Dict): Data containing the virtual machine ID.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: Response from the service layer indicating the result of the
                detachment.
        """
        LOG.info('Call service layer on attach image.')
        detach_info.update({'image_id': image_id, 'user_info': user_info})
        result: Dict = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.detach_image.__name__,
            data_for_method=detach_info,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result
