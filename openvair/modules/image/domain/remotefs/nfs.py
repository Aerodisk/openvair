"""Module for handling image operations on an NFS (Network File System).

This module provides the `NfsImage` class, which represents an image stored
on an NFS and includes methods for uploading, deleting, and attaching
information about the image.

Classes:
    NfsImage: Represents an image stored on an NFS with methods for performing
        file operations related to the image.
"""

from typing import Any, Dict
from pathlib import Path

from openvair.config import TMP_DIR
from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.image.domain.base import BaseRemoteFSImage

LOG = get_logger(__name__)


class NfsImage(BaseRemoteFSImage):
    """Class representing an NFS image."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initializes a new instance of the NfsImage class.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self._execute_as_root = False
        LOG.info('Initialized NfsImage.')

    def upload(self) -> Dict:
        """Uploads the image to the specified path on NFS.

        This method converts the image file to the QCOW2 format using the
        `qemu-img` utility and moves it to the specified directory on the NFS.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        LOG.info(f'Uploading image with ID {self.id}')
        image_path = Path(self.path, f'image-{self.id}')
        image_tmp = Path(TMP_DIR, self.name)
        try:
            execute(
                'qemu-img',
                'convert',
                '-f raw',
                '-O qcow2',
                image_tmp,  # type: ignore
                image_path,  # type: ignore
            )
        except Exception as e:
            LOG.exception(f'Failed to upload image with ID {self.id}:')
            LOG.error(e)
            raise
        else:
            LOG.info(f'Image with ID {self.id} uploaded successfully')
        return self.__dict__

    def delete(self) -> Dict:
        """Deletes the image from the specified path on NFS.

        This method removes the image file from the NFS.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        LOG.info('Deleting NFSImage...')
        image_path = f'{self.path}/image-{self.id}'
        execute('rm', '-f', image_path, run_as_root=self._execute_as_root)
        LOG.info('NFSImage successfully deleted.')
        return self.__dict__

    def delete_from_tmp(self) -> Dict:
        """Deletes the image from the temporary directory.

        This method removes the image file from the temporary directory.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        LOG.info('Deleting NFSImage from temporary directory...')
        image_tmp = Path(TMP_DIR, self.name)
        execute('rm', '-f', image_tmp, run_as_root=self._execute_as_root)  # type: ignore
        LOG.info('NFSImage successfully deleted from temporary directory.')
        return self.__dict__

    def attach_image_info(self) -> Dict:
        """Attaches the image information to the object.

        This method checks if the image exists on the NFS and then returns its
        path and size.

        Returns:
            Dict: A dictionary containing the image's path and size.
        """
        LOG.info('Attaching info to NFSImage...')
        self._check_image_exists()
        LOG.info('Info successfully attached to NFSImage.')
        return {'path': f'{self.path}/image-{self.id}', 'size': self.size}
