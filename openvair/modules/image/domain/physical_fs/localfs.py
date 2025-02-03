"""Module for handling image operations on the local file system.

This module provides the `LocalFSImage` class, which represents an image
stored on the local file system and includes methods for uploading, deleting,
and attaching information about the image.

Classes:
    LocalFSImage: Represents an image stored on the local file system, with
        methods for performing file operations related to the image.
"""

from typing import Any, Dict
from pathlib import Path

from openvair.config import TMP_DIR
from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.image.domain.base import BaseLocalFSImage

LOG = get_logger(__name__)


class LocalFSImage(BaseLocalFSImage):
    """Class representing an image stored on the local file system."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initializes a `LocalFSImage` instance.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.
        """
        super(LocalFSImage, self).__init__(*args, **kwargs)
        self._execute_as_root = False
        LOG.info('Initialized LocalImage.')

    def upload(self) -> Dict:
        """Uploads the image to the local file system.

        This method converts the image file to the QCOW2 format using the
        `qemu-img` utility and moves it to the specified directory.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        LOG.info('Uploading LocalFSImage...')
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
            msg = f'Image with ID {self.id} uploaded successfully'
            LOG.info(msg)
        return self.__dict__

    def delete(self) -> Dict:
        """Deletes the image from the local file system.

        This method removes the image file from the file system. If the image
        does not exist, it logs an exception.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        LOG.info('Deleting LocalFSImage...')
        try:
            self._check_image_exists()
        except Exception as _:
            LOG.exception("LocalFSImage doesn't exist on storage.")
            raise
        else:
            try:
                image_path = f'{self.path}/image-{self.id}'
                execute(
                    'rm', '-f',
                    image_path,
                    params=ExecuteParams(
                        run_as_root=self._execute_as_root,
                        raise_on_error=True
                    )
                )
            except (ExecuteError, OSError) as err:
                msg = f'Failed to delete image with ID {self.id}: {err}'
                LOG.exception(msg)
                raise

            LOG.info('LocalFSImage successfully deleted.')
            return self.__dict__

    def delete_from_tmp(self) -> Dict:
        """Deletes the image from the temporary directory.

        This method removes the image file from the temporary directory.

        Returns:
            Dict: A dictionary containing the image's attributes.
        """
        LOG.info('Deleting LocalFSImage from temporary directory...')
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
                f'Failed to delete image with ID {self.id} '
                f'from temporary directory: {err}'
            )
            LOG.exception(msg)
            raise

        LOG.info('LocalFSImage successfully deleted from temporary directory.')
        return self.__dict__

    def attach_image_info(self) -> Dict:
        """Attaches information about the local image.

        This method checks if the image exists and then returns its path
        and size.

        Returns:
            Dict: A dictionary containing the image's path and size.
        """
        LOG.info('Attaching info to LocalFSImage...')
        self._check_image_exists()
        LOG.info('Info successfully attached to LocalFSImage.')
        return {'path': f'{self.path}/image-{self.id}', 'size': self.size}
