"""Adapter for interacting with qemu-img by executing shell commands.

This module provides the `QemuImgAdapter` class, which encapsulates domain logic
for disk image operations such as creation, conversion, validation, and info
retrieval.

Classes:
    QemuImgAdapter: Adapter class for managing qcow2/raw disk operations.
"""

from typing import Dict
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecutionResult
from openvair.libs.qemu_img.executor import QemuImgCommandExecutor
from openvair.libs.qemu_img.exceptions import QemuImgError
from openvair.libs.data_handlers.json.serializer import deserialize_json

LOG = get_logger(__name__)


class QemuImgAdapter:
    """Encapsulates domain logic for qemu-img operations.

    This class provides methods for working with qcow2/raw files using qemu-img.

    Attributes:
        executor (QemuImgCommandExecutor): Command executor for qemu-img.
    """

    INFO_SUBCOMMAND = 'get_info'
    CHECK_SUBCOMMAND = 'check_valid'
    CREATE_BACKING_SUBCOMMAND = 'create_backing_volume'
    CONVERT_SUBCOMMAND = 'create_copy'
    DELETE_SUBCOMMAND = 'delete'

    def __init__(self) -> None:
        """Initialize a QemuImgAdapter instance.

        Sets up the internal command executor used for running qemu-img
        operations.
        """
        self.executor = QemuImgCommandExecutor()

    def get_info(self, image_path: Path) -> Dict:
        """Retrieves detailed information about a disk image.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            Dict: Parsed output of `qemu-img info --output=json`

        Raises:
            QemuImgError: If command fails.
        """
        result = self.executor.execute(f'info --output=json {image_path}')
        self._check_result(self.INFO_SUBCOMMAND, result)
        info: Dict = deserialize_json(result.stdout)
        return info

    def check_valid(self, image_path: Path) -> bool:
        """Checks integrity of an image file.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            bool: True if valid, False if invalid.
        """
        result = self.executor.execute(f'check {image_path}')
        return result.returncode == 0

    def create_backing_volume(
        self,
        backing_path: Path,
        target_path: Path,
    ) -> None:
        """Creates a new qcow2 volume using a backing file.

        Args:
            backing_path (Path): Path to the backing qcow2 file.
            target_path (Path): Path for the new image file.

        Raises:
            QemuImgError: If creation fails.
        """
        result = self.executor.execute(
            f'create -f qcow2 -b {backing_path} {target_path}'
        )
        self._check_result(self.CREATE_BACKING_SUBCOMMAND, result)

    def create_copy(
        self,
        source_path: Path,
        target_path: Path,
        fmt: str = 'qcow2',
    ) -> None:
        """Creates a full copy of an image file.

        Args:
            source_path (Path): Path to the source image.
            target_path (Path): Path to the target image.
            fmt (str): Output format, default is 'qcow2'.

        Raises:
            QemuImgError: If convert fails.
        """
        result = self.executor.execute(
            f'convert -O {fmt} {source_path} {target_path}'
        )
        self._check_result(self.CONVERT_SUBCOMMAND, result)

    def delete(self, image_path: Path) -> None:
        """Deletes an image file from disk.

        Args:
            image_path (Path): Path to the image file.

        Raises:
            QemuImgError: If deletion fails.
        """
        try:
            Path(image_path).unlink()
        except OSError as e:
            message: str = f'Failed to delete image: {e}'
            raise QemuImgError(message) from e

    def _check_result(
        self,
        subcommand: str,
        result: ExecutionResult,
    ) -> None:
        """Check command result and raise an error if it failed.

        Args:
            subcommand (str): Subcommand being performed.
            result (ExecutionResult): Result object of the executed command.

        Raises:
            QemuImgError: If the command failed.
        """
        if result.returncode != 0:
            message: str = (
                f'Operation "{subcommand}" failed with code '
                f'{result.returncode}.'
                f'\n\tstderr: {result.stderr}'
            )
            raise QemuImgError(message)
