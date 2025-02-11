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
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
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
            LOG.info('Converting image to QCOW2 format...')
            execute(
                'qemu-img',
                'convert',
                '-f raw',
                '-O qcow2',
                str(image_tmp),
                str(image_path),
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    run_as_root=self._execute_as_root,
                    raise_on_error=True
                )
            )
            LOG.info('Image converted successfully')
        except (ExecuteError, OSError) as err:
            msg = f'Failed to upload image with ID {self.id}: {err}'
            LOG.exception(msg)
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
        image_path = Path(self.path, f'image-{self.id}')

        try:
            execute(
                'rm',
                '-f',
                str(image_path),
                params=ExecuteParams(
                    run_as_root=self._execute_as_root,
                    raise_on_error=True
                )
            )
        except (ExecuteError, OSError) as err:
            msg = f'Failed to delete image with ID {self.id}: {err}'
            LOG.exception(msg)
            raise

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
        try:
            execute(
                'rm',
                '-f',
                str(image_tmp),
                params=ExecuteParams(
                    run_as_root=self._execute_as_root,
                    raise_on_error=True
                )
            )
        except (ExecuteError, OSError) as err:
            msg = (
                f'Failed to delete image with ID {self.id} from '
                f'temporary directory: {err}'
            )
            LOG.exception(msg)
            raise

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
