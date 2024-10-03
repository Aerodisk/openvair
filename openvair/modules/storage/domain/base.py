"""Module for defining base classes for storage and partition management.

This module provides abstract base classes for managing different types of
storage and partitions. It includes implementations for specific storage types
like remote and local file systems, and defines the interface for interacting
with partitioned storage.

Classes:
    BaseStorage: Abstract base class for storage management.
    RemoteFSStorage: Class for managing remote file system storage.
    LocalFSStorage: Class for managing local file system storage.
    BasePartition: Abstract base class representing a partitioned storage.
"""

import abc
import uuid
from typing import Dict, List, Optional
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.storage.config import STORAGE_DATA
from openvair.modules.storage.domain.utils import PartedParser
from openvair.modules.storage.adapters.parted import PartedAdapter
from openvair.modules.storage.domain.remotefs.exceptions import (
    PackageIsNotInstalled,
)

LOG = get_logger(__name__)


class BaseStorage(metaclass=abc.ABCMeta):
    """Abstract base class for storage management.

    This class defines the interface for managing various types of storage,
    including setup, creation, deletion, and retrieving capacity information.

    Attributes:
        name (str): The name of the storage.
        description (str): A brief description of the storage.
        storage_type (str): The type of storage (e.g., 'remotefs', 'localfs').
        id (str): Unique identifier for the storage.
        initialized (bool): Whether the storage has been initialized.
    """

    def __init__(self, **kwargs):
        """Initialize the BaseStorage with given parameters.

        Args:
            kwargs: Arbitrary keyword arguments for initializing the storage
                attributes.
        """
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.storage_type = kwargs.get('storage_type', '')
        self.id = str(kwargs.get('id', uuid.uuid4()))
        self.initialized = kwargs.get('initialized', False)

    @abc.abstractmethod
    def do_setup(self) -> Dict:
        """Perform any necessary setup for the storage.

        Returns:
            Dict: Setup details or results.
        """
        ...

    @abc.abstractmethod
    def create(self) -> Dict:
        """Create the storage.

        Returns:
            Dict: Details of the created storage.
        """
        ...

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the storage."""
        ...

    @abc.abstractmethod
    def get_capacity_info(self) -> Dict:
        """Retrieve capacity information for the storage.

        Returns:
            Dict: Capacity details.
        """
        ...


class RemoteFSStorage(BaseStorage):
    """Class for managing remote file system storage.

    This class provides methods to handle remote file system storage, including
    mounting shares and managing storage capacity.

    Attributes:
        share (str): The share path of the remote file system.
        _mounted_shares (List[str]): List of currently mounted shares.
        _execute_as_root (bool): Whether to execute commands as root.
        reserved_percentage (int): Percentage of storage reserved.
        storage_prefix (str): Prefix used for the storage mount point.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the RemoteFSStorage with given parameters.

        Args:
            args: Positional arguments passed to the BaseStorage initializer.
            kwargs: Keyword arguments passed to the BaseStorage initializer.
        """
        super(RemoteFSStorage, self).__init__(*args, **kwargs)
        self.share = ''
        self._mounted_shares: List[str] = []
        self._execute_as_root = True
        self.reserved_percentage = 10
        self.storage_prefix = 'remotefs'

    def do_setup(self) -> Dict:
        """Perform any initialization required by the volume driver.

        Returns:
            Dict: Details of the setup process.
        """
        self._check_or_create_path(self.mount_point_path())
        self._ensure_share_mounted()

    def create(self) -> Dict:
        """Create the remote file system storage.

        Returns:
            Dict: Details of the created storage.
        """
        return self._create()

    def delete(self) -> None:
        """Delete the remote file system storage."""
        self._delete()

    def get_capacity_info(self) -> Dict:
        """Retrieve capacity information for the remote file system storage.

        Returns:
            Dict: Capacity details.
        """
        return self._get_capacity_info()

    def _create(self) -> Dict:
        """Internal method to create the storage.

        Returns:
            Dict: Details of the created storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def _delete(self) -> None:
        """Internal method to delete the storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def _get_capacity_info(self) -> Dict:
        """Internal method to retrieve capacity information.

        Returns:
            Dict: Capacity details.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def mount_point_name(self) -> str:
        """Generate the mount point name for the storage.

        Returns:
            str: The generated mount point name.
        """
        return f'{self.storage_type}-{self.id}'

    def mount_point_path(self) -> Path:
        """Generate the mount point path for the storage.

        Returns:
            Path: The generated mount point path.
        """
        return STORAGE_DATA.joinpath('mnt', self.mount_point_name())

    @staticmethod
    def _check_or_create_path(path: Path) -> None:
        """Check if a path exists, and create it if it does not.

        Args:
            path (Path): The path to check or create.
        """
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)

    def _ensure_share_mounted(self) -> Dict:
        """Ensure that the remote share is mounted.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @staticmethod
    def _check_package_is_installed(package: str) -> None:
        """Check if a package is installed on the system.

        Args:
            package (str): The name of the package to check.

        Raises:
            Exception: If the package is not installed.
        """
        out, err = execute(package, run_as_root=False)
        if not out:
            raise PackageIsNotInstalled(package)


class LocalFSStorage(BaseStorage):
    """Class for managing local file system storage.

    This class provides methods to handle local file system storage, including
    formatting and mounting the storage.

    Attributes:
        _execute_as_root (bool): Whether to execute commands as root.
        storage_prefix (str): Prefix used for the storage mount point.
        fs_type (str): The file system type (e.g., "ext4", "xfs").
    """

    def __init__(self, *args, **kwargs):
        """Initialize the LocalFSStorage with given parameters.

        Args:
            args: Positional arguments passed to the BaseStorage initializer.
            kwargs: Keyword arguments passed to the BaseStorage initializer.
        """
        super().__init__(*args, **kwargs)
        self._execute_as_root = True
        self.storage_prefix = 'localfs'
        self.fs_type = kwargs.get('fs_type')  # "ext4"|"xfs"

    def do_setup(self) -> Dict:
        """Perform any initialization required by the volume.

        Returns:
            Dict: Details of the setup process.
        """
        self._check_or_create_path(self.mount_point_path())
        if not self.initialized:
            self.formatting()
        self._ensure_storage_mounted()

    def create(self) -> Dict:
        """Create the local file system storage.

        Returns:
            Dict: Details of the created storage.
        """
        return self._create()

    def delete(self) -> None:
        """Delete the local file system storage."""
        self._delete()

    def get_capacity_info(self) -> Dict:
        """Retrieve capacity information for the local file system storage.

        Returns:
            Dict: Capacity details.
        """
        return self._get_capacity_info()

    def _create(self) -> Dict:
        """Internal method to create the storage.

        Returns:
            Dict: Details of the created storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def _delete(self) -> None:
        """Internal method to delete the storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def _get_capacity_info(self) -> Dict:
        """Internal method to retrieve capacity information.

        Returns:
            Dict: Capacity details.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def mount_point_name(self) -> str:
        """Generate the mount point name for the storage.

        Returns:
            str: The generated mount point name.
        """
        return f'{self.storage_type}-{self.id}'

    def mount_point_path(self) -> Path:
        """Generate the mount point path for the storage.

        Returns:
            Path: The generated mount point path.
        """
        return STORAGE_DATA.joinpath('mnt', self.mount_point_name())

    @staticmethod
    def _check_or_create_path(path: Path) -> None:
        """Check if a path exists, and create it if it does not.

        Args:
            path (Path): The path to check or create.
        """
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)

    def _ensure_storage_mounted(self) -> None:
        """Ensure that the local storage is mounted.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @staticmethod
    def _check_package_is_installed(package: str) -> None:
        """Check if a package is installed on the system.

        Args:
            package (str): The name of the package to check.

        Raises:
            Exception: If the package is not installed.
        """
        try:
            out, err = execute(
                'dpkg', '-l', '|', 'grep', package, run_as_root=False
            )
            if not out:
                raise PackageIsNotInstalled(package)
        except OSError as _:
            ...

    def formatting(self) -> None:
        """Format the local storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


class BasePartition(metaclass=abc.ABCMeta):
    """Abstract base class representing a partitioned storage.

    This class defines the interface for interacting with a partitioned storage,
    including methods for creating, deleting, editing partitions, and obtaining
    partition information.

    Attributes:
        parted_adapter (PartedAdapter): Object for interacting with the parted
            utility.
        partitions (Dict): A dictionary containing information about partitions
            on the storage.
    """

    def __init__(self, **kwargs):
        """Initialize the BasePartition with given parameters.

        Args:
            kwargs: Arbitrary keyword arguments for initializing the partition
                attributes.
        """
        self.parted_adapter = PartedAdapter(kwargs.get('local_disk_path', ''))
        self.parted_parser = PartedParser()
        self.partitions: Dict

    @abc.abstractmethod
    def create_partition(self, data: Dict) -> Optional[int]:
        """Create a partition on the storage.

        Args:
            data (Dict): Data required for creating a partition.

        Returns:
            Optional[int]: The partition number if created successfully,
                otherwise None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_partition(self, data: Dict) -> None:
        """Delete a partition from the storage.

        Args:
            data (Dict): Data required for deleting a partition.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_partitions_info(self) -> Dict:
        """Get information about partitions on the storage.

        Returns:
            Dict: Partition information.
        """
        raise NotImplementedError
