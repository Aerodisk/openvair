"""Module for managing image-related operations in the service layer.

This module provides functionality for handling image operations such as
uploading, retrieving, and managing image metadata. It serves as an
intermediary between the API layer and the domain layer, coordinating
image-related tasks and managing database interactions.

The module includes classes for representing image statuses and a manager
class for handling image operations. It also defines named tuples for
storing image and storage information.

Classes:
    ImageStatus: Enum representing the possible status values for an image.
    ImageServiceLayerManager: Manager class for handling image-related
        operations in the service layer.

Named tuples:
    ImageInfo: Stores information about an image, including name, size,
        description, storage ID, and user ID.
    StorageInfo: Stores information about a storage, including ID, name,
        type, status, available space, and mount point.

The module interacts with the domain layer via RPC calls and uses a
unit of work pattern for database operations. It also integrates with
an event store for logging significant events related to image operations.

Constants:
    TMP_DIR: Directory for temporary storage of images during processing.
    API_SERVICE_LAYER_QUEUE_NAME: Name of the queue for API service layer
        communication.
    SERVICE_LAYER_DOMAIN_QUEUE_NAME: Name of the queue for domain layer
        communication.

This module is designed to be used as part of a larger system for managing
virtual machine images and related resources.
"""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Dict, List, NoReturn, Optional, cast
from pathlib import Path
from collections import namedtuple

from openvair.config import TMP_DIR
from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks, periodic_task
from openvair.modules.image.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.image.domain.base import BaseImage
from openvair.modules.image.adapters.orm import Image, ImageAttachVM
from openvair.modules.image.service_layer import exceptions, unit_of_work
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.image.adapters.serializer import DataSerializer
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.libs.messaging.clients.rpc_clients.storage_rpc_client import (
    StorageServiceLayerRPCClient,
)

if TYPE_CHECKING:
    from openvair.abstracts.base_exception import BaseCustomException

LOG = get_logger(__name__)


ImageInfo = namedtuple(
    'ImageInfo',
    [
        'name',
        'size',
        'description',
        'storage_id',
        'user_id',
    ],
)


StorageInfo = namedtuple(
    'StorageInfo',
    ['id', 'name', 'storage_type', 'status', 'available_space', 'mount_point'],
)


class ImageStatus(enum.Enum):
    """Enum representing the possible status values for an image.

    This enum defines the various states an image can be in throughout its
    lifecycle in the system. It helps in tracking and managing the current
    state of an image during operations such as upload, deletion, and error
    handling.

    Attributes:
        new (int): Indicates that the image has been newly created or registered
            in the system but not yet processed.
        uploading (int): Represents that the image is currently in the process
            of being uploaded to the storage.
        available (int): Signifies that the image has been successfully uploaded
            and is ready for use.
        error (int): Indicates that an error occurred during image processing
            or management.
        deleting (int): Represents that the image is in the process of being
            deleted from the system.

    The integer values associated with each status are used for ordering and
    can be helpful in database representations or API responses.
    """

    new = 1
    uploading = 2
    available = 3
    error = 4
    deleting = 5


class ImageServiceLayerManager(BackgroundTasks):
    """Manager class for handling image-related operations in the service layer.

    This class serves as the main entry point for image management operations,
    coordinating interactions between the API layer, domain layer, and database.
    It handles tasks such as image creation, retrieval, deletion, and status
    management.

    The class inherits from BackgroundTasks, allowing it to perform periodic
    or background operations related to image management.

    Attributes:
        uow (SqlAlchemyUnitOfWork): Unit of work for managing database
            transactions.
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
            with the API of service layer.
        storage_serviece_rpc (RabbitRPCClient): RPC client for communicating
            with the storage service layer.
        event_store (EventCrud): Event store for logging image-related events.

    The class provides methods for various image operations, including error
    handling and interaction with external services like storage management.
    """

    def __init__(self) -> None:
        """Initialize the ImageServiceLayerManager.

        This constructor sets up the necessary components for the
        ImageServiceLayerManager, including:
        - Initializing the parent BackgroundTasks class
        - Setting up the unit of work for database operations
        - Configuring RPC clients for communication with domain and service
            layers
        - Initializing the event store for logging events

        The initialization ensures that the manager is ready to handle
        image-related operations and maintain proper communication channels
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
        self.storage_service_client = StorageServiceLayerRPCClient()
        self.event_store: EventCrud = EventCrud('image')

    def _call_domain_delete_from_tmp(
        self,
        db_image: Image,
        message: str,
    ) -> None:
        """Call the domain layer to delete a temporary image file.

        This method sets the image status to 'error', updates the image
        information with the provided message, converts the database image
        record to a domain representation, and calls the domain layer to
        delete the temporary image file.

        Args:
            db_image (Image): The database image record associated with the
                temporary file.
            message (str): The error message to be set for the image.
        """
        db_image.status = ImageStatus.error.name
        db_image.information = message
        domain_image = DataSerializer.to_domain(db_image)
        self.domain_rpc.call(
            BaseImage.delete_from_tmp.__name__,
            data_for_manager=domain_image,
        )

    def _handle_create_image_rpc_exceptions(
        self,
        db_image: Image,
        err: BaseCustomException,
    ) -> NoReturn:
        """Handle RPC exceptions during image creation and clean up tmp files.

        This method is called when an RPC exception occurs during the image
        creation process, specifically when calling the domain layer. It sets an
        error status and message for the database image record, calls the domain
        layer to delete the temporary image file, and re-raises the exception
        with an updated message.

        Args:
            db_image (Image): The database image record associated with the
                error.
            err (Exception): The RPC exception that occurred during image
                creation.

        Raises:
            Exception: The original RPC exception with an updated message.
        """
        message = (
            'An error occurred when calling the domain layer while '
            f'creating image: {err!s}'
        )
        self._call_domain_delete_from_tmp(db_image, message)
        err.message = message
        raise err

    def _handle_create_image_exceptions(
        self,
        db_image: Image,
        err: BaseCustomException,
    ) -> NoReturn:
        """Handle exceptions during image creation and clean up temporary files.

        This method is called when an exception occurs during the image creation
        process. It sets an error status and message for the database image
        record, calls the domain layer to delete the temporary image file,
        and re-raises the exception with an updated message.

        Args:
            db_image (Image): The database image record associated with the
                error.
            err (Exception): The exception that occurred during image creation.

        Raises:
            Exception: The original exception with an updated message.
        """
        message = f'An error occurred while creating image: {err!s}'
        self._call_domain_delete_from_tmp(db_image, message)
        LOG.error(message)
        err.message = message
        raise err

    def get_image(self, data: Dict) -> Dict:
        """Retrieve a specific image from the database.

        This method fetches an image from the database based on the provided
        image ID and returns its serialized representation.

        Args:
            data (Dict): A dictionary containing the image ID.

        Returns:
            Dict: A dictionary representing the serialized image with its
                metadata.

        Raises:
            UnexpectedDataArguments: If the provided data is missing the image
                ID.
        """
        LOG.info('Service Layer start handling response on get image.')
        image_id = data.pop('image_id', None)
        LOG.debug(f'Get image id from request: {image_id}.')
        if not image_id:
            message = (
                'Incorrect arguments were received '
                f'in the request get image: {data}.'
            )
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        with self.uow:
            image = self.uow.images.get(image_id)
            serialized_image = DataSerializer.to_web(image)
            LOG.debug(f'Got image from db: {serialized_image}.')
        LOG.info('Service Layer method get image was successfully processed.')
        return serialized_image

    def get_all_images(self, data: Dict) -> List:
        """Retrieve all images from the database.

        This method fetches all available images from the database and returns
        them as a list of serialized image dictionaries.

        Args:
            data (Dict): A dictionary containing optional request data, such as
                the storage ID for filtering images by storage.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary represents
                a serialized image with its metadata.
        """
        LOG.info('Service Layer start handling response on get images.')
        storage_id = data.pop('storage_id', None)
        with self.uow:
            if storage_id:
                images = self.uow.images.get_all_by_storage(storage_id)
            else:
                images = self.uow.images.get_all()
            LOG.debug(f'Got images from db: {images}')
            serialized_images = [
                DataSerializer.to_web(image) for image in images
            ]
        LOG.info('Service Layer method get images was successfully processed.')
        return serialized_images

    @staticmethod
    def _check_image_status(
        image_status: Optional[str], available_statuses: List[str]
    ) -> None:
        """Check if an image's status is valid.

        This method verifies if the provided image status is among the list
        of available (valid) statuses. If the status is invalid, it raises
        an ImageStatusError exception.

        Args:
            image_status (str): The status of the image to check.
            available_statuses (List[str]): A list of valid image statuses.

        Raises:
            exceptions.ImageStatusError: If the image status is invalid.
        """
        if image_status not in available_statuses:
            message: str = (
                f'Image status is {image_status} but '
                f'must be in {available_statuses}'
            )
            LOG.info(message)
            raise exceptions.ImageStatusError(message)

    @staticmethod
    def _check_image_has_not_attachment(image: Image) -> None:
        """Check if an image has no attachments.

        This method verifies if the provided image has no attachments
        (e.g., virtual machines). If the image has attachments, it raises
        an ImageHasAttachmentError exception.

        Args:
            image (Image): The image to check for attachments.

        Raises:
            exceptions.ImageHasAttachmentError: If the image has attachments.
        """
        if image.attachments:
            message = f'Image {image.id} has attachments.'
            LOG.error(message)
            raise exceptions.ImageHasAttachmentError(message)

    def _get_storage_info(self, storage_id: str) -> StorageInfo:
        """Retrieve information about a storage.

        This method fetches information about a storage with the specified
        ID from the storage service layer. If an error occurs during the
        retrieval process, it returns a default StorageInfo object with
        empty values.

        Args:
            storage_id (str): The ID of the storage to retrieve information for.

        Returns:
            StorageInfo: A named tuple containing information about the storage
        """
        try:
            storage_info = self.storage_service_client.get_storage(
                {'storage_id': str(storage_id)}
            )
        except (RpcCallException, RpcCallTimeoutException) as err:
            message = f'An error occurred when getting storages: {err!s}'
            LOG.error(message)
            return StorageInfo(
                id='',
                name='',
                storage_type='',
                status='',
                available_space=0,
                mount_point='',
            )
        storage_extra_specs = storage_info.get('storage_extra_specs', {})
        return StorageInfo(
            id=storage_info.get('id'),
            name=storage_info.get('name'),
            storage_type=storage_info.get('storage_type'),
            status=storage_info.get('status'),
            available_space=int(storage_info.get('available', 0)),
            mount_point=storage_extra_specs.get('mount_point', ''),
        )

    @staticmethod
    def _check_storage_on_availability(storage: StorageInfo) -> None:
        """Check if the specified storage is available.

        Args:
            storage (StorageInfo): The storage to check.

        Raises:
            exceptions.StorageUnavailableException: If the storage is not
                available.
        """
        if storage.status != 'available':
            message = (
                f'Storage {storage.name} status is '
                f'{storage.status} but must be available'
            )
            LOG.error(message)
            raise exceptions.StorageUnavailableException(message)

    @staticmethod
    def _check_available_space_on_storage(
        image_size: Optional[int], storage: StorageInfo
    ) -> None:
        """Check if there is enough available space on the specified storage.

        Args:
            image_size (int): The size of the image to check.
            storage (StorageInfo): The storage to check.

        Raises:
            exceptions.ValidateArgumentsError: If there is not enough available
                space on the storage.
        """
        if image_size >= storage.available_space:
            message = (
                'Not enough available space on the ' f'storage {storage.id}.'
            )
            LOG.error(message)
            raise exceptions.ValidateArgumentsError(message)

    @staticmethod
    def _prepare_image_data(image_info: Dict) -> ImageInfo:
        """Create and return an ImageInfo object for uploading

        It takes a dictionary of image information, and returns a ImageInfo
        object

        Args:
            image_info (Dict): The data that comes from the user.

        Returns:
            ImageInfo: An object containing the prepared image data.

        Raises:
            UnexpectedDataArguments: If the provided data is invalid or missing
                required fields.
        """
        LOG.info('Start preparing information for creating image in db.')
        image = ImageInfo(
            size=Path(f'{TMP_DIR}/{image_info["name"]}').stat().st_size,
            name=image_info.pop('name', ''),
            description=image_info.pop('description', ''),
            storage_id=image_info.pop('storage_id', ''),
            user_id=image_info.pop('user_id', ''),
        )
        LOG.debug('Image Info for creating: %s.' % image._asdict())
        if not (image_info or image.size or image.storage_id):
            message = 'Comes unexpected data for uploading image.'
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        LOG.info('Image info was successfully prepared.')
        return image

    def upload_image(self, image_info: Dict) -> Dict:
        """Upload a new image to the system.

        This method handles the initial process of uploading an image. It
        prepares the image data, checks for existing images with the same name,
        creates a new database entry for the image, and initiates the
        asynchronous image creation process.

        Args:
            image_info (Dict): A dictionary containing information about the
                image to be uploaded. This should include details such as the
                image name, size, description, storage ID, and user information.

        Returns:
            Dict: A dictionary containing the serialized image information,
                including the newly assigned image ID.

        Raises:
            UploadImageDataError: If the provided image information is empty or
                invalid.
            ImageNameExistsException: If an image with the same name already
                exists in the system.
        """
        LOG.info('Service Layer start handling response on upload image.')
        user_info = image_info.pop('user_info', {})
        user_id = user_info.get('id', '')
        if not image_info:
            message = f'Got empty info about upload image {image_info}.'
            LOG.error(message)
            raise exceptions.UploadImageDataError(message)
        name = image_info.get('name', '')

        image_info.update({'user_id': user_id})
        image = self._prepare_image_data(image_info)

        with self.uow:
            LOG.info('Preparing image_info for db table Image.')

            # check if image with this name already exists
            if self.uow.images.get_by_name(image.name):
                self._delete_image_from_tmp(name)
                raise exceptions.ImageNameExistsException(image.name)

            db_image: Image = cast(Image, DataSerializer.to_db(image._asdict()))
            db_image.status = ImageStatus.new.name
            LOG.info('Start inserting image into db with status new.')
            self.uow.images.add(db_image)
            self.uow.commit()
            serialized_image = DataSerializer.to_web(db_image)
            LOG.debug(
                'Serialized image ready for other steps: %s' % serialized_image
            )

        LOG.info('Cast _create_image for other steps.')
        serialized_image.update({'user_info': user_info})
        self.service_layer_rpc.cast(
            self._create_image.__name__, data_for_method=serialized_image
        )

        message = 'Image was uploaded successfully'
        LOG.info(message)
        self.event_store.add_event(
            str(db_image.id), user_id, self.upload_image.__name__, message
        )
        return serialized_image

    def _delete_image_from_tmp(self, name: str) -> None:
        tmp_path = Path(TMP_DIR, name)
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            LOG.warning(f"Unable to remove tmp image '{tmp_path}'")

    def _create_image(self, image_info: Dict) -> None:
        """Create an image in the system asynchronously.

        This method is called asynchronously after the initial upload_image
        process. It handles the actual creation of the image, including storage
        checks, domain layer interactions, and status updates. The method
        updates the image status in the database and logs events to the event
        store.

        Args:
            image_info (Dict): A dictionary containing detailed information
                about the image to be created, including image ID, storage ID,
                and user information.
        """
        LOG.info('Service Layer start handling response on _create_image.')

        image_id = image_info.get('id', '')
        user_info = image_info.pop('user_info', {})
        user_id = user_info.get('id', '')
        storage_id = image_info.get('storage_id', '')
        storage_info = self._get_storage_info(str(storage_id))

        with self.uow:
            db_image = self.uow.images.get(uuid.UUID(image_id))
            LOG.info('Got image from db: %s.' % db_image)

            try:
                self._check_image_status(
                    db_image.status, [ImageStatus.new.name]
                )
                self._check_storage_on_availability(storage_info)
                self._check_available_space_on_storage(
                    db_image.size, storage_info
                )
                db_image.status = ImageStatus.uploading.name
                db_image.path = storage_info.mount_point
                db_image.storage_type = storage_info.storage_type
                self.uow.commit()

                domain_image = DataSerializer.to_domain(db_image)
                LOG.info(
                    'Serialized image which will call to domain '
                    'for uploading: %s.' % domain_image
                )
                LOG.info('Cast upload on domain.')

                self.domain_rpc.call(
                    BaseImage.upload.__name__,
                    data_for_manager=domain_image,
                    time_limit=360,
                )
                message = 'Image was created successfully'
                LOG.info(message)
                self.event_store.add_event(
                    image_id, user_id, self._create_image.__name__, message
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    'An error occurred when calling the domain layer while '
                    f'creating image: {err!s}'
                )
                self.event_store.add_event(
                    image_id,
                    user_id,
                    self._create_image.__name__,
                    message,
                )
                self._handle_create_image_rpc_exceptions(db_image, err)
            except (
                exceptions.ImageStatusError,
                exceptions.ValidateArgumentsError,
                exceptions.StorageUnavailableException,
            ) as err:
                message = f'An error occurred while creating image: {err!s}'
                self.event_store.add_event(
                    image_id, user_id, self._create_image.__name__, message
                )
                self._handle_create_image_exceptions(db_image, err)
            finally:
                self._delete_image_from_tmp(image_info.get('name', ''))
                db_image.status = ImageStatus.available.name
                self.uow.commit()
                LOG.debug('Image status was updated on %s.' % db_image.status)

        LOG.info(
            'Service Layer method _create_image was successfully processed'
        )

    def delete_image(self, data: Dict) -> Dict:
        """Service method for deleting an image.

        This method deletes an image from the database and initiates the
        process of deleting the image from the image domain.

        Args:
            data (Dict): Data for deleting the image, including user info
                and image ID.
        """
        LOG.info('Service Layer start handling response on delete image.')
        user_info = data.pop('user_info', {})
        image_id = data.get('image_id', '')

        with self.uow:
            db_image = self.uow.images.get(image_id)
            available_statuses = [
                ImageStatus.available.name,
                ImageStatus.error.name,
            ]
            try:
                self._check_image_status(db_image.status, available_statuses)
                self._check_image_has_not_attachment(db_image)

                db_image.status = ImageStatus.deleting.name
                self.uow.commit()

                domain_image = DataSerializer.to_domain(db_image)
                domain_image.update({'user_info': user_info})
                LOG.debug('Got image from db: %s.' % domain_image)

                self.service_layer_rpc.cast(
                    self._delete_image.__name__, data_for_method=domain_image
                )
                return DataSerializer.to_web(db_image)
            except (
                exceptions.ImageStatusError,
                exceptions.ImageHasAttachmentError,
            ) as err:
                message = (
                    'An error occurred when deleting the ' f'image: {err!s}'
                )
                db_image.status = ImageStatus.error.name
                db_image.information = message
                LOG.error(message)
                raise exceptions.ImageDeletingError(message)
            finally:
                self.uow.commit()

    def _delete_image(self, image_info: Dict) -> None:
        """Deletes an image and its associated data from the database.

        This method deletes an image from the database and calls the domain
        layer to delete the image from the storage. It also handles various
        exceptions that may occur during the deletion process.

        Args:
            image_info (Dict): Information about the image.

        Raises:
            RpcCallException: If an error occurs when calling the domain layer.
            RpcCallTimeoutException: If a timeout occurs when calling the domain
                layer.
            StorageUnavailableException: If the storage is not available.
            ImageDeletingError: If an error occurs during the image deletion
                process.
        """
        image_id = image_info.get('id', '')
        user_info = image_info.pop('user_info')
        user_id = user_info.get('id', '')

        with self.uow:
            db_image = self.uow.images.get(image_id)

            try:
                if db_image.storage_type:
                    self.domain_rpc.call(
                        BaseImage.delete.__name__, data_for_manager=image_info
                    )
                self.uow.session.delete(db_image)
                self.uow.commit()
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    'An error occurred when calling the '
                    f'domain layer while deleting image: {err!s}'
                )
                self.event_store.add_event(
                    image_id, user_id, self._delete_image.__name__, message
                )
                db_image.information = message or ''
                db_image.status = (
                    ImageStatus.error.name
                    if message
                    else ImageStatus.available.name
                )
                self.uow.commit()
                LOG.error(message)
                raise exceptions.ImageDeletingError(message)

        message = 'Image was deleted successfully'

        LOG.info(message)

        self.event_store.add_event(
            image_id, user_id, self._delete_image.__name__, message
        )

    @staticmethod
    def _check_image_has_same_attachment(
        image_attachments: List,
        new_attachment: Dict,
    ) -> None:
        """Checks if the image already has an attachment to a VM.

        Args:
            image_attachments (List): List of the image's attachments.
            new_attachment (Dict): The new attachment to be checked.

        Raises:
            ImageHasSameAttachment: If the image already has an attachment
                with the same `vm_id`.
        """
        vm_id = new_attachment.get('vm_id', '')
        for attachment in image_attachments:
            if attachment.vm_id == vm_id:
                message = f'Image already has attachment for VM with id {vm_id}'
                LOG.error(message)
                raise exceptions.ImageHasSameAttachment(message)

    def attach_image(
        self, data: Dict
    ) -> Dict:  # TODO: need to refactor this method
        """Attaches an image to a virtual machine.

        This method attaches an image to a virtual machine by adding the
        attachment information to the database and calling the domain layer
        to perform the necessary operations.

        Args:
            data (Dict): Information about the image attachment.

        Raises:
            RpcCallException: If an error occurs when calling the domain layer.
            RpcCallTimeoutException: If a timeout occurs when calling the domain
                layer.
            ImageStatusError: If the image status is not available.

        Returns:
            Dict: The result of the domain layer call for attaching the image.
        """
        LOG.info('Starting attach image to vm.')
        with self.uow:
            db_image = self.uow.images.get(data.get('image_id'))  # type: ignore
            available_statuses = [ImageStatus.available.name]
            try:
                self._check_image_status(db_image.status, available_statuses)
                self._check_image_has_same_attachment(
                    db_image.attachments, data
                )
                attachment = DataSerializer.to_db(data, ImageAttachVM)
                db_image.attachments.append(attachment)  # type: ignore
                serialized_image = DataSerializer.to_domain(db_image)
                attach_result: Dict = self.domain_rpc.call(
                    BaseImage.attach_image_info.__name__,
                    data_for_manager=serialized_image,
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    'An error occurred when calling the '
                    f'domain layer while attaching image: {err!s}'
                )
                db_image.status = ImageStatus.error.name
                db_image.information = message
                raise
            except exceptions.ImageStatusError as err:
                message = 'An error occurred while attaching ' f'image: {err!s}'
                LOG.error(str(err) + message)
                db_image.status = ImageStatus.error.name
                db_image.information = message
                raise
            else:
                db_image.status = ImageStatus.available.name
                db_image.information = ''
                self.uow.commit()
                LOG.info('Image was successfully attached.')
                return attach_result

    def detach_image(self, data: Dict) -> Dict:
        """Detaches an image from a virtual machine.

        This method detaches an image from a virtual machine by removing the
        attachment information from the database and performing any necessary
        cleanup operations.

        Args:
            data (Dict): Information about the image and VM to detach.

        Raises:
            ImageStatusError: If the image status is not valid.

        Returns:
            Dict: The updated image information after detaching.
        """
        LOG.info('Starting detaching image from vm.')
        image_id = data.get('image_id', '')
        vm_id = data.get('vm_id', '')
        with self.uow:
            db_image = self.uow.images.get(image_id)
            available_statuses = [
                ImageStatus.available.name,
                ImageStatus.error.name,
            ]
            try:
                self._check_image_status(db_image.status, available_statuses)
                for attachment in db_image.attachments:
                    if str(attachment.vm_id) == vm_id:
                        db_image.attachments.remove(attachment)
                        self.uow.session.delete(attachment)
                LOG.info('Image was successfully detached.')
            except exceptions.ImageStatusError as err:
                message = 'An error occurred while detaching ' f'image: {err!s}'
                db_image.status = ImageStatus.error.name
                db_image.information = message
                LOG.exception(message)
                raise err  # noqa: TRY201 need to handle concrete exception
            finally:
                self.uow.commit()
        return DataSerializer.to_web(db_image)

    def _get_all_storages_info(self) -> List[StorageInfo]:
        """Get information about all available storage devices.

        Returns:
            List[StorageInfo]: A list of objects representing the available
                storage devices.
        """
        LOG.info('Collecting storages information...')

        prepared_storages: List[StorageInfo] = []
        try:
            storages = self.storage_service_client.get_all_storages()
        except Exception as err:  # noqa: BLE001 Need to catch concrete exception
            LOG.error(f'An error occurred when getting storages: {err!s}')
            return prepared_storages

        LOG.info(f'Retrieved information for {len(storages)} storages.')
        for storage in storages:
            storage_extra_specs = storage.get('storage_extra_specs', {})
            prepared_storages.append(
                StorageInfo(
                    id=storage.get('id'),
                    name=storage.get('name'),
                    storage_type=storage.get('storage_type'),
                    status=storage.get('status'),
                    available_space=int(storage.get('available', 0)),
                    mount_point=storage_extra_specs.get('mount_point', ''),
                )
            )
        LOG.info(f'Prepared information for {len(prepared_storages)} storages.')

        LOG.info('Storages information collected successfully')
        return prepared_storages

    @periodic_task(interval=10)
    def monitoring(self) -> None:
        """Method for periodic monitoring of images.

        This method is responsible for periodically monitoring the status of
        images in the system. It retrieves all images from the database, checks
        their status and the availability of their associated storage, and
        updates the image information accordingly.

        The method performs the following steps:

        1. Retrieve all images from the database and convert them to domain
            objects.
        2. Get information about all available storage devices.
        3. For each image:
        - Retrieve the storage information for the image.
        - Validate the image status and storage availability.
        - Get updated image information from the domain layer.
        - Update the image information in a list for subsequent database update.
        - Handle any exceptions that occur during the process.
        4. Update the image information in the database in bulk.

        This method is designed to run periodically using the `@periodic_task`
        decorator, with an interval of 10 seconds.

        Args:
            self: The instance of the `ImageServiceLayerManager` class.

        Returns:
            None

        Raises:
            RpcCallException: If an error occurs while calling the domain layer.
            RpcCallTimeoutException: If the timeout waiting for a response from
                the domain layer expires.
            ImageHasNotStorage: If the image does not have an associated
                storage.
            StorageUnavailableException: If the storage associated with the
                image is unavailable.
            ImageStatusError: If the image status is not valid for monitoring.
        """
        LOG.info('Start monitoring.')
        monitoring_statuses: List[str] = [
            ImageStatus.available.name,
            ImageStatus.error.name,
        ]
        domain_images = self._get_domain_images()
        if not domain_images:
            LOG.info("Stop monitoring. Images don't exist.")
            return

        storages = self._get_available_storages()
        updated_images = []
        for domain_image in domain_images:
            LOG.info(f'Checking image: {domain_image["name"]}')
            image_status = domain_image.get('status', '')
            try:
                LOG.info(f'Current image status: {image_status}')
                self._check_image_status(image_status, monitoring_statuses)
            except exceptions.ImageStatusError:
                LOG.info('Its not for monitoring, going to next image..')
                continue

            try:
                image_storage = self._get_image_storage(domain_image, storages)
                self._validate_image_and_storage(domain_image, image_storage)
                updated_image = self._update_image_info(domain_image)
                updated_images.append(updated_image)
            except (
                exceptions.ImageHasNotStorage,
                exceptions.StorageUnavailableException,
                exceptions.ImageUnvailableError,
                RpcCallException,
                RpcCallTimeoutException,
            ) as err:
                self._handle_monitoring_error(domain_image, err)
            LOG.info(f'{domain_image["name"]} was checked')
        self._update_images_in_db(updated_images)
        LOG.info('Stop monitoring.')

    def _get_domain_images(self) -> List[Dict]:
        """Get all images from the database and convert to domain objects."""
        with self.uow:
            db_images = self.uow.images.get_all()
            return [DataSerializer.to_domain(img) for img in db_images]

    def _get_available_storages(self) -> Dict[str, StorageInfo]:
        """Get information about all available storage devices."""
        storages = self._get_all_storages_info()
        return {storage.id: storage for storage in storages}

    def _get_image_storage(
        self, domain_image: Dict, storages: Dict[str, StorageInfo]
    ) -> StorageInfo:
        """Get the storage information for the given image."""
        storage_id = domain_image['storage_id']
        image_storage = storages[storage_id]
        if not image_storage:
            raise exceptions.ImageHasNotStorage(str(domain_image.get('id')))
        return image_storage

    def _validate_image_and_storage(
        self, domain_image: Dict, image_storage: StorageInfo
    ) -> None:
        """Validate the image and storage availability."""
        self._check_storage_on_availability(image_storage)
        self._check_image_on_availability(domain_image)

    def _check_image_on_availability(self, domain_image: Dict) -> None:
        """Trying to find image by path

        Args:
            domain_image (Dict): dict with image info

        Raises:
            exceptions.ImageUnvailableError: when cannot find image by its path
        """
        image_path: str = str(domain_image.get('path'))
        LOG.info(
            f'Checking availability for {domain_image["name"]}'
            f'by path: {image_path}'
        )
        if not Path(image_path).exists():
            message = f'image_id {domain_image["id"]}, path: {image_path}'
            raise exceptions.ImageUnvailableError(message)

    def _update_image_info(self, domain_image: Dict) -> Dict:
        """Get updated image information from the domain layer."""
        result = self.domain_rpc.call(
            BaseImage.attach_image_info.__name__, data_for_manager=domain_image
        )
        return {
            'id': domain_image.get('id'),
            'size': result.get('size', domain_image['size']),
            'status': ImageStatus.available.name,
            'information': '',
        }

    def _handle_monitoring_error(
        self, domain_image: Dict, err: Exception
    ) -> None:
        """Handle errors during image monitoring."""
        message = self._get_monitoring_error_message(err)
        LOG.error(message)
        self._update_image_status_on_error(domain_image, message)

    def _get_monitoring_error_message(self, err: Exception) -> str:
        """Get the error message for the monitoring error."""
        if isinstance(err, (RpcCallException, RpcCallTimeoutException)):
            return f'An error occurred while calling the domain layer: {err!s}.'
        if isinstance(
            err,
            (
                exceptions.ImageHasNotStorage,
                exceptions.StorageUnavailableException,
            ),
        ):
            return f'An error occurred while accessing the storage: {err!s}.'
        if isinstance(err, exceptions.ImageStatusError):
            return str(err)
        return str(err)

    def _update_image_status_on_error(
        self, domain_image: Dict, message: str
    ) -> None:
        """Update the image status and information on error."""
        updated_image = {
            'id': domain_image.get('id'),
            'status': ImageStatus.error.name,
            'information': message,
        }
        self._update_images_in_db([updated_image])

    def _update_images_in_db(self, updated_images: List[Dict]) -> None:
        """Update the image information in the database."""
        with self.uow:
            self.uow.images.bulk_update(updated_images)
            self.uow.commit()
