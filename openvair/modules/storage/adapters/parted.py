"""Module for interacting with the `parted` utility.

This module provides a class `PartedAdapter` that offers methods to interact
with the `parted` utility for disk partitioning. It supports creating,
printing, and removing partitions.

Classes:
    PartedAdapter: A class providing methods to interact with the parted
        utility.
"""

from typing import Dict

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.modules.storage.adapters import exceptions

LOG = get_logger(__name__)


class PartedAdapter:
    """A class providing methods to interact with the parted utility.

    This class includes methods for creating, printing, and removing partitions
    using the parted utility.

    Attributes:
        disk_path (str): The path to the disk to be manipulated.
    """

    def __init__(self, disk_path: str):
        """Initialize PartedAdapter with the disk path.

        Args:
            disk_path (str): The path to the disk to be manipulated.
        """
        self.disk_path = disk_path

    def mkpart(self, start_part: str, end_part: str) -> Dict[str, str]:
        """Create a partition using parted.

        Args:
            start_part (str): The start position of the partition.
            end_part (str): The end position of the partition.

        Returns:
            Dict[str, str]: A dictionary containing stdout and stderr messages.

        Raises:
            PartedError: If an error occurs during partition creation.
        """
        command = (
            f'parted {self.disk_path} -s mkpart '
            f'primary {start_part} {end_part}'
        )

        exec_result = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if 'error' in exec_result.stderr.lower():
            stderr = exec_result.stderr
            LOG.error(f'Error occurred during partition creation: {stderr}')
            raise exceptions.PartedError(stderr)

        LOG.info(f'Partition created successfully: {exec_result.stdout}')
        return {'stdout': exec_result.stdout, 'stderr': exec_result.stderr}

    def print(self, *, free: bool = True) -> str:
        """Print partition information using parted.

        Args:
            free (bool): Whether to include free space information.

        Returns:
            str: The output of the print command.

        Raises:
            PartedError: If an error occurs during partition printing or
                disk table creation.
        """
        free_arg = 'free' if free else ''
        print_command = f'parted -s {self.disk_path} unit B print {free_arg}'
        exec_result = execute(
            print_command,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
            ),
        )
        if exec_result.stderr:
            LOG.error(
                f'Error occurred during partition print: {exec_result.stderr}'
            )

            LOG.info('Try running create disk table')
            init_label_command = f'parted -s {self.disk_path} mktable gpt '
            exec_result = execute(
                init_label_command,
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    run_as_root=True,
                ),
            )
            if exec_result.stderr:
                stderr = exec_result.stderr
                msg = f'Error during mktable partition creation: {stderr}'
                LOG.error(msg)
                raise exceptions.PartedError(msg)
            LOG.info('Disk table created successfully')

            LOG.info('Creating partition using parted again.')
            exec_result = execute(
                print_command,
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    run_as_root=True,
                ),
            )
            if exec_result.stderr:
                stderr = exec_result.stderr
                msg = f'Error occurred during partition print: {stderr}'
                LOG.error(msg)
                raise exceptions.PartedError(msg)

        return exec_result.stdout

    def rm(self, partition_number: str) -> None:
        """Remove a partition using parted.

        Args:
            partition_number (str): The number of the partition to remove.

        Raises:
            PartedError: If an error occurs during the removal process.
        """
        command = f'parted -s {self.disk_path} rm {partition_number!s}'
        exec_result = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
            ),
        )
        if 'error' in exec_result.stderr.lower():
            LOG.error(
                f'Error occurred during partition removal: {exec_result.stderr}'
            )
            raise exceptions.PartedError(exec_result.stderr)

        LOG.info(f'Partition removed successfully: {exec_result.stdout}')
