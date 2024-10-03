"""Base classes for handling images in the domain layer.

This module provides abstract base classes for representing and managing
images stored on local and remote file systems. It defines a common interface
for operations such as uploading, deleting, and attaching information to
images, as well as checking the existence of an image on the storage.

Classes:
    BaseImage: Abstract base class for all image types, defining common
        attributes and methods.
    BaseRemoteFSImage: Abstract base class for images stored on remote file
        systems.
    BaseLocalFSImage: Abstract base class for images stored on the local file
        system.
"""

import abc
from typing import Dict
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.modules.image.domain import exceptions

LOG = get_logger(__name__)


class BaseImage(metaclass=abc.ABCMeta):
    """Abstract base class for all image types.

    This class defines common attributes and methods that are shared among
    different image storage implementations, such as local and remote file
    systems.
    """

    def __init__(self, **kwargs):
        """Initializes a `BaseImage` instance with common attributes.

        Args:
            kwargs: Arbitrary keyword arguments containing image attributes.
        """
        LOG.info('Initialized BaseImage.')
        self.id = str(kwargs.get('id', ''))
        self.size = kwargs.get('size', '0')
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.storage_type = kwargs.get('storage_type', '')
        self.path = kwargs.get('path', '')

    @abc.abstractmethod
    def upload(self) -> Dict:
        """Uploads the image.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        ...

    @abc.abstractmethod
    def delete(self) -> Dict:
        """Deletes the image.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        ...

    @abc.abstractmethod
    def attach_image_info(self) -> Dict:
        """Attaches information about the image.

        Returns:
            Dict: A dictionary containing the image's path and size.
        """
        ...

    @abc.abstractmethod
    def delete_from_tmp(self) -> Dict:
        """Deletes the image from the temporary directory.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        ...

    def _check_image_exists(self) -> None:
        """Checks if the image exists on the storage.

        Raises:
            ImageDoesNotExistOnStorage: If the image does not exist at the
                specified path.
        """
        image_path = Path(self.path) / f'image-{self.id}'
        if not image_path.exists():
            raise exceptions.ImageDoesNotExistOnStorage(self.id)


class BaseRemoteFSImage(BaseImage):
    """Abstract base class for images stored on remote file systems.

    This class extends `BaseImage` and provides a template for implementing
    operations specific to images stored on remote file systems.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a `BaseRemoteFSImage` instance."""
        LOG.info('Initialized RemoteFSImage')
        super(BaseRemoteFSImage, self).__init__(*args, **kwargs)

    def upload(self) -> Dict:
        """Uploads the image.

        Returns:
            Dict: A dictionary containing the image's attributes.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def delete(self) -> Dict:
        """Deletes the image.

        Returns:
            Dict: A dictionary containing the image's attributes.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def attach_image_info(self) -> Dict:
        """Attaches information about the image.

        Returns:
            Dict: A dictionary containing the image's path and size.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def delete_from_tmp(self) -> Dict:
        """Deletes the image from the temporary directory.

        Returns:
            Dict: A dictionary containing the image's attributes.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError


class BaseLocalFSImage(BaseImage):
    """Abstract base class for images stored on the local file system.

    This class extends `BaseImage` and provides a template for implementing
    operations specific to images stored on local file systems.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a `BaseLocalFSImage` instance."""
        super(BaseLocalFSImage, self).__init__(*args, **kwargs)

    def upload(self) -> Dict:
        """Uploads the image.

        Returns:
            Dict: A dictionary containing the image's attributes.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def delete(self) -> Dict:
        """Deletes the image.

        Returns:
            Dict: A dictionary containing the image's attributes.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def attach_image_info(self) -> Dict:
        """Attaches information about the image.

        Returns:
            Dict: A dictionary containing the image's path and size.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def delete_from_tmp(self) -> Dict:
        """Deletes the image from the temporary directory.

        Returns:
            Dict: A dictionary containing the image's attributes.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError
