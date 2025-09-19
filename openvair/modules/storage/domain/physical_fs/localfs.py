"""Module for managing local filesystem storage and partitions.

This module provides classes and methods for interacting with local filesystem
storage and managing disk partitions. It includes functionality for setting up
storage, formatting disks, and creating, deleting, and retrieving partition
information.

Classes:
    LocalDiskStorage: A class for managing local filesystem storage.
    LocalPartition: A class for managing partitions on local disks.
"""

from typing import Any

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.storage.domain import exception as exc
from openvair.modules.storage.domain.base import BasePartition, LocalFSStorage
from openvair.modules.storage.domain.utils import DiskSizeValueObject
from openvair.modules.storage.domain.physical_fs.exceptions import UnmountError

LOG = get_logger(__name__)


class LocalDiskStorage(LocalFSStorage):
    """Class for managing local filesystem storage.

    This class provides methods for initializing, setting up, formatting,
    and retrieving information about local storage.

    Attributes:
        path (str): The path to the local file system.
        fs_type (str): The file system type (e.g., xfs, ext4).
        fs_uuid (str): The UUID of the file system.
        mount_point (str): The mount point for the file system.
        _execute_as_root (bool): Flag to determine if commands should
            be executed as root.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a new instance of LocalDiskStorage.

        This constructor initializes the LocalDiskStorage instance with
        the provided path, file system type, and any additional arguments.

        Args:
            args: Variable length argument list, passed to the parent class.
            kwargs: Arbitrary keyword arguments, including:
                path (str): The path to the local file system.
                fs_type (str): The file system type (e.g., xfs, ext4).
                fs_uuid (str): The UUID of the file system.
        """
        LOG.info('LocalFS storage initializing')
        super(LocalDiskStorage, self).__init__(*args, **kwargs)
        self._execute_as_root = True
        self.path = str(kwargs.get('path', ''))
        self.fs_uuid = kwargs.get('fs_uuid', '')
        self.mount_point = str(self.mount_point_path())
        self.do_setup()

    def do_setup(self) -> dict:
        """Set up the local filesystem storage.

        This method ensures that the necessary packages are installed,
        the storage is mounted, and the capacity information is retrieved.

        Returns:
            Dict: The instance's dictionary representation.
        """
        LOG.info('LocalFS storage do setup')
        if self.fs_type == 'xfs':
            self._check_package_is_installed('xfsprogs')
        super(LocalDiskStorage, self).do_setup()
        self.get_capacity_info()
        return self.__dict__

    def _ensure_storage_mounted(self) -> None:
        """Mount the storage to the mount point."""
        LOG.info(f'Mounting storage to {self.mount_point} directory...')
        execute(
            'mount',
            self.path,
            self.mount_point,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
            ),
        )

    def _get_fs_uuid(self) -> str:
        """Get the UUID of the file system.

        Returns:
            str: The UUID of the file system.
        """
        LOG.info('Getting UUID of the file system...')
        exec_result = execute(
            'blkid',
            self.path,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
            ),
        )
        return exec_result.stdout.split('"')[1]

    def _create(self) -> dict:
        """Create the storage by retrieving its UUID.

        Returns:
            Dict: The instance's dictionary representation.
        """
        self.fs_uuid = self._get_fs_uuid()
        return self.__dict__

    def _delete(self) -> None:
        """Unmount the storage and delete the mount point."""
        try:
            LOG.info(f'Unmounting storage from {self.mount_point} directory...')
            execute(
                'umount',
                self.mount_point,
                params=ExecuteParams(  # noqa: S604
                    shell=True, run_as_root=True, raise_on_error=True
                ),
            )
            LOG.info(f'Deleting {self.mount_point} directory...')
            execute(
                'rm',
                '-rf',
                self.mount_point,
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    run_as_root=True,
                    raise_on_error=True,
                ),
            )
        except (ExecuteError, OSError) as e:
            LOG.warning(f'Error during unmounting storage - {e}')
            raise UnmountError(str(e))

    def _get_capacity_info(self) -> dict:
        """Get the size and available space of the storage.

        Returns:
            str: The instance's dictionary representation.
        """
        LOG.info('Getting the size and available space of the storage...')
        try:
            exec_result = execute(
                'df',
                '--portability',
                '--block-size',
                '1',
                self.mount_point,
                params=ExecuteParams(  # noqa: S604
                    run_as_root=False,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except (ExecuteError, OSError) as err:
            LOG.error(err)
            raise
        out = exec_result.stdout.splitlines()[1]

        self.size = int(out.split()[1])
        self.available = int(out.split()[3])
        return self.__dict__

    def _format_xfs(self, disk_path: str) -> None:
        """Format the disk with the XFS file system.

        Args:
            disk_path (str): The path to the disk.
        """
        LOG.info(f'Formatting the disk with XFS file system at {disk_path}...')
        execute(
            'mkfs.xfs',
            '-f',
            disk_path,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=self._execute_as_root,
            ),
        )

    def _format_ext4(self, disk_path: str) -> None:
        """Format the disk with the EXT4 file system.

        Args:
            disk_path (str): The path to the disk.
        """
        LOG.info(f'Formatting the disk with EXT4 file system at {disk_path}...')
        execute(
            'mkfs.ext4',
            '-F',
            disk_path,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=self._execute_as_root,
            ),
        )

    def formatting(self) -> None:
        """Format the storage according to its file system type."""
        if self.fs_type == 'xfs':
            self._format_xfs(self.path)
        elif self.fs_type == 'ext4':
            self._format_ext4(self.path)
        else:
            raise NotImplementedError


class LocalPartition(BasePartition):
    """A class representing a local partitioned storage.

    This class provides methods for creating, deleting, editing partitions,
    and obtaining partition information for a local disk.

    Attributes:
        partitions (Dict): A dictionary containing information about partitions
            on the storage.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a new instance of LocalPartition."""
        super().__init__(*args, **kwargs)
        self.partitions: dict = self._get_partitions_info()

    def create_partition(self, data: dict) -> int | None:
        """Create a partition on the local disk.

        Args:
            data (Dict): Data for creating the partition, including start and
                end points.

        Returns:
            Optional[int]: Number of the new partition.
        """
        LOG.info('Start creating partition on local disk.')

        creating_size = DiskSizeValueObject(
            value=data['size_value'], unit=data['size_unit']
        )
        creating_bounds = self._calculate_creating_bounds(creating_size)

        self.parted_adapter.mkpart(
            str(creating_bounds.get('start')),
            str(creating_bounds.get('end')),
        )

        new_partitions = self._get_partitions_info()
        part_num = None
        for part in new_partitions.values():
            # find new partition and return
            if (
                part['File system'] != 'Free Space'
                and part not in self.partitions.values()
            ):
                part_num = part['Number']
                LOG.info('Finish creating partition on local disk.')
        return part_num

    def delete_partition(self, data: dict) -> None:
        """Delete a partition from the local disk.

        Args:
            data (Dict): Data containing the partition number to be deleted.
        """
        LOG.info('Start deleting partition on local disk.')
        partition_number = data.pop('partition_number')
        self.parted_adapter.rm(partition_number)
        LOG.info('Finish deleting partition on local disk.')

    def get_partitions_info(self) -> dict:
        """Retrieve information about partitions on the local disk.

        Returns:
            Dict: A dictionary containing information about partitions.
        """
        return self._get_partitions_info()

    def _get_partitions_info(self) -> dict:
        """Get information about partitions on the local disk.

        Returns:
            Dict: Information about partitions on the local disk.
        """
        LOG.info('Getting partitions info from local disk.')
        print_stdout = self.parted_adapter.print()
        return self.parted_parser.parse_partitions_info(print_stdout)

    def _calculate_creating_bounds(
        self, creating_value: DiskSizeValueObject
    ) -> dict[str, DiskSizeValueObject]:
        """Calculate bounds for creating a new partition.

        Args:
            creating_value (DiskSizeValueObject): The value representing
                the size of the partition to be created.

        Returns:
            Dict[str, DiskSizeValueObject]: Dictionary containing information
                about the start and end of the partition size.
        """
        LOG.debug('Calculating creating partition resource availability.')

        available_space_info: dict = self._get_partitions_info().popitem()[1]
        if available_space_info.get('File system') != 'Free Space':
            message = 'Disk has no free space'
            LOG.error(message)
            raise exc.WrongPartitionRangeError(message)

        available_space = str(available_space_info.get('Size'))
        available_start_bound = str(available_space_info.get('Start'))
        available_end_bound = str(available_space_info.get('End'))

        byte_creating_space = self.parted_parser.get_byte_value(
            str(creating_value)
        )
        byte_available_space = self.parted_parser.get_byte_value(
            available_space
        )
        byte_available_start = self.parted_parser.get_byte_value(
            available_start_bound
        )
        byte_available_end = self.parted_parser.get_byte_value(
            available_end_bound
        )

        calculated_end = byte_available_start + byte_creating_space - 1
        if (
            byte_creating_space > byte_available_space
            or calculated_end > byte_available_end
        ):
            message = (
                f"it's impossible to create a partition with this volume: "
                f'{creating_value}, available size: '
                f'{byte_available_space}B'
            )
            LOG.error(message)
            raise exc.WrongPartitionRangeError(message)

        creating_bounds: dict[str, DiskSizeValueObject] = {
            'start': DiskSizeValueObject(value=byte_available_start, unit='B'),
            'end': DiskSizeValueObject(value=calculated_end, unit='B'),
        }

        return creating_bounds
