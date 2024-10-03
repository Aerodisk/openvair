"""Module for managing NFS volumes.

This module provides classes and methods for creating, deleting, and managing
NFS volumes in a virtualized environment.

Classes:
    NfsVolume: Class for managing NFS volumes.
"""

from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.volume.domain.base import RemoteFSVolume
from openvair.modules.volume.domain.remotefs import exceptions

LOG = get_logger(__name__)


class NfsVolume(RemoteFSVolume):
    """Class for managing NFS volumes.

    This class provides methods for creating, deleting, extending, and
    retrieving information about NFS volumes.
    """

    def __init__(self, *args, **kwargs):
        """Initialize an instance of the NfsVolume class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        LOG.info('Initialized NfsVolume')
        super(NfsVolume, self).__init__(*args, **kwargs)
        self._execute_as_root = False
        self.provisioning = 'metadata'

    def create(self) -> Dict:
        """Create a new NFS volume.

        Raises:
            QemuImgCreateException: If there's an error while creating
                the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        preallocation = self.provisioning if self.format != 'raw' else 'off'
        volume_path = f'{self.path}/volume-{self.id}'
        _, err = execute(
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
        if err:
            message = f'Qemu img create raised exception: {err!s}'
            LOG.error(message)
            raise exceptions.QemuImgCreateException(message)
        LOG.info(f'Created volume {volume_path}')
        return self.__dict__

    def delete(self) -> Dict:
        """Delete an existing NFS volume.

        Raises:
            DeleteVolumeException: If there's an error while deleting
                the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        volume_path = f'{self.path}/volume-{self.id}'
        _, err = execute(
            'rm', '-f', volume_path, run_as_root=self._execute_as_root
        )
        if err:
            message = f'Delete volume raised exception: {err!s}'
            LOG.error(message)
            raise exceptions.DeleteVolumeException(message)
        LOG.info(f'Deleted volume {volume_path}')
        return self.__dict__

    def extend(self, new_size: str) -> Dict:
        """Extend the size of an existing NFS volume.

        Args:
            new_size (str): The new size of the volume.

        Raises:
            QemuImgExtendException: If there's an error while extending
                the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        self._check_volume_exists()
        volume_path = f'{self.path}/volume-{self.id}'
        _, err = execute(
            'qemu-img',
            'resize',
            volume_path,
            new_size,
            run_as_root=self._execute_as_root,
        )
        if err:
            message = f'Qemu img extend volume raised exception: {err!s}'
            LOG.error(message)
            raise exceptions.QemuImgExtendException(message)
        LOG.info(f'Extended volume {volume_path} to size {new_size}')
        return self.__dict__

    def attach_volume_info(self) -> Dict:
        """Get information about the NFS volume.

        Returns:
            Dict: A dictionary containing information about the volume.
        """
        self._check_volume_exists()
        qemu_volume_info = self._get_info_about_volume()
        LOG.info(f'Attached info about volume {self.id}')
        return {
            'path': f'{self.path}/volume-{self.id}',
            'size': qemu_volume_info.get('virtual-size', self.size),
            'used': qemu_volume_info.get('actual-size', 0),
            'provisioning': self.provisioning,
        }
