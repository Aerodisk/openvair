"""Module for managing local filesystem volumes.

This module provides classes and methods for creating, deleting, and managing
local filesystem volumes in a virtualized environment.

Classes:
    BaseLocalFSVolume: Base class for local filesystem volumes.
    LocalFSVolume: Class for managing local filesystem volumes.
"""

from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.volume.domain.base import BaseVolume

LOG = get_logger(__name__)


class BaseLocalFSVolume(BaseVolume):
    """Base class for local filesystem volumes.

    This class provides a base implementation for managing volumes stored on
    local filesystems.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a BaseLocalFSVolume instance."""
        super(BaseLocalFSVolume, self).__init__(*args, **kwargs)

    def create(self) -> Dict:
        """Create a new volume.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def delete(self) -> Dict:
        """Delete an existing volume.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def extend(self, new_size: int) -> Dict:
        """Extend an existing volume to the given size.

        Args:
            new_size (int): The new size for the volume.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def attach_volume_info(self) -> Dict:
        """Get information about an existing volume.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError


class LocalFSVolume(BaseLocalFSVolume):
    """Class for managing local filesystem volumes.

    This class provides methods for creating, deleting, and managing local
    filesystem volumes.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a LocalFSVolume instance."""
        super(LocalFSVolume, self).__init__(*args, **kwargs)
        self._execute_as_root = False
        self.provisioning = 'metadata'

    def create(self) -> Dict:
        """Create a new volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        LOG.info(
            f'Creating volume with id={self.id}, path={self.path},'
            f'size={self.size}, format={self.format}'
        )
        preallocation = self.provisioning if self.format != 'raw' else 'off'
        volume_path = f'{self.path}/volume-{self.id}'
        execute(
            'qemu-img',
            'create',
            '-f',
            self.format,
            '-o',
            f'preallocation={preallocation}',
            volume_path,
            self.size,
            run_as_root=self._execute_as_root,
        )
        return self.__dict__

    def delete(self) -> Dict:
        """Delete an existing volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        LOG.info(f'Deleting volume with id={self.id}, path={self.path}')
        volume_path = f'{self.path}/volume-{self.id}'
        execute('rm', '-f', volume_path, run_as_root=self._execute_as_root)
        return self.__dict__

    def extend(self, new_size: str) -> Dict:
        """Extend an existing volume to the given size.

        Args:
            new_size (str): The new size for the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        LOG.info(
            f'Extending volume with id={self.id},'
            f'path={self.path} to new size={new_size}'
        )
        self._check_volume_exists()
        volume_path = f'{self.path}/volume-{self.id}'
        execute(
            'qemu-img',
            'resize',
            volume_path,
            new_size,
            run_as_root=self._execute_as_root,
        )
        return self.__dict__

    def attach_volume_info(self) -> Dict:
        """Get information about an existing volume.

        Returns:
           Dict: A dictionary containing information about the volume.
        """
        LOG.info(f'Getting info for volume with id={self.id}, path={self.path}')
        self._check_volume_exists()
        qemu_volume_info = self._get_info_about_volume()
        return {
            'path': f'{self.path}/volume-{self.id}',
            'size': qemu_volume_info.get('virtual-size', self.size),
            'used': qemu_volume_info.get('actual-size', 0),
            'provisioning': self.provisioning,
        }
