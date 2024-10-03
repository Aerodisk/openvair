"""Module for managing NFS (Network File System) storage operations.

This module defines the `NfsStorage` class, which extends the `RemoteFSStorage`
class to provide functionality specific to NFS storage. The class handles
operations such as mounting NFS shares, checking NFS availability, retrieving
storage capacity, and other necessary management tasks.

Classes:
    NfsStorage: Represents and manages a network file system (NFS) storage.
"""

import os
import re
from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import ExecuteTimeoutExpiredError, execute
from openvair.modules.storage.domain.base import RemoteFSStorage
from openvair.modules.storage.domain.remotefs.exceptions import (
    NFSCantBeMountError,
    GettinStorageInfoError,
    NfsIpIsNotAvailableError,
    NfsPathDoesNotExistOnShareError,
)

LOG = get_logger(__name__)


class NfsStorage(RemoteFSStorage):
    """Represents a network file system (NFS) storage.

    This class extends the `RemoteFSStorage` base class and provides
    methods for managing an NFS storage system, including mounting
    the storage, checking availability, and retrieving capacity information.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the NFS storage.

        This constructor initializes the NFS storage with the specified
        IP address, path, and mount version.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, including:
                - ip (str): The IP address of the NFS server.
                - path (str): The file path on the NFS server.
                - mount_version (int): The NFS mount version (default is 4).
        """
        super(NfsStorage, self).__init__(*args, **kwargs)
        self._execute_as_root = True
        self.ip = kwargs.get('ip', '')
        self.path = kwargs.get('path', '')
        self.mount_version = kwargs.get('mount_version', 4)
        self.base = ''
        self.mount_point = str(self.mount_point_path())
        self.share = f'{self.ip}:{self.path}'

    def do_setup(self) -> Dict:
        """Performs any necessary setup steps for the NFS storage.

        This method checks if the required NFS package is installed,
        performs the parent class setup, and retrieves the storage
        capacity information.

        Returns:
            Dict: The attributes of the NFS storage.
        """
        LOG.info('Starting do_setup method.')
        self._check_package_is_installed('mount.nfs')
        super(NfsStorage, self).do_setup()
        self.get_capacity_info()
        LOG.info('Finished do_setup method.')
        return self.__dict__

    def _ensure_share_mounted(self) -> None:
        """Mounts the NFS share to the mount point.

        This method mounts the NFS share to the specified mount point
        if it is not already mounted.

        Raises:
            NFSCantBeMountError: If the NFS share cannot be mounted within
            the specified timeout.
        """
        LOG.info('Starting mounting NFS share.')
        if not os.path.ismount(self.mount_point):
            LOG.info('Starting mount command.')
            try:
                out, _ = execute(
                    'mount',
                    '-t',
                    'nfs',
                    '-o',
                    f'vers={self.mount_version},async,nolock',
                    self.share,
                    self.mount_point,
                    timeout=2,
                    run_as_root=False,
                )
            except ExecuteTimeoutExpiredError:
                msg = f"Nfs {self.share} can't be mount."
                raise NFSCantBeMountError(msg)
            else:
                LOG.debug(out)
        LOG.info('Finished mounting NFS share.')

    def _check_ip_and_path(self) -> None:
        """Checks if the NFS IP address and path are available.

        This method verifies that the specified IP address and path
        on the NFS server are accessible.

        Raises:
            NfsIpIsNotAvailableError: If the NFS IP address is not available.
            NfsPathDoesNotExistOnShareError: If the specified path does not
            exist on the NFS share.
        """
        LOG.info('Starting _check_ip_and_path method.')
        try:
            output, _ = execute('showmount', '-e', self.ip, timeout=3)
            if 'Export list' not in output:
                raise NfsIpIsNotAvailableError(self.ip)
        except ExecuteTimeoutExpiredError:
            message = f'Nfs ip {self.ip} is not available'
            LOG.error(message)
            raise NfsIpIsNotAvailableError(message)
        available_paths = re.findall(r'\n(.*?)\s', output)
        if self.path not in available_paths:
            message = f"Nfs doesn't have current path {self.path}."
            LOG.error(message)
            raise NfsPathDoesNotExistOnShareError(message)
        LOG.info('Finished _check_ip_and_path method.')

    def _create(self) -> Dict:
        """Creates the NFS storage.

        By checking the IP address and path, setting it up, and returning its
        attributes

        Returns:
            Dict: The attributes of the NFS storage.
        """
        LOG.info('Starting _create method.')
        self._check_ip_and_path()
        self.do_setup()
        LOG.info('Finished _create method.')
        return self.__dict__

    def _delete(self) -> None:
        """Unmounts the storage and then deletes the mount point.

        This method unmounts the NFS share from the mount point and
        deletes the mount point directory.
        """
        LOG.info('Starting _delete method.')
        execute('umount', self.mount_point, run_as_root=False)
        execute('rm', '-rf', self.mount_point, run_as_root=False)
        LOG.info('Finished _delete method.')

    def _get_capacity_info(self) -> Dict:
        """Retrieves the capacity of the NFS storage.

        This method gets the total size and available space of the
        mounted NFS storage.

        Returns:
            Dict: The attributes of the NFS storage, including size
            and available space.

        Raises:
            GettinStorageInfoError: If the storage information cannot be
            retrieved.
        """
        LOG.info('Starting _get_capacity_info method.')
        out, err = execute(
            'df',
            '--portability',
            '--block-size',
            '1',
            self.mount_point,
            run_as_root=False,
        )
        if err:
            msg = "Can't get info about storage."
            raise GettinStorageInfoError(msg)
        out = out.splitlines()[1]

        self.size = int(out.split()[1])
        self.available = int(out.split()[3])
        LOG.info('Finished _get_capacity_info method.')
        return self.__dict__
