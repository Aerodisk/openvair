"""Adapter for interacting with restic by executing bash command.

This module provides the `ResticAdapter` class, which is used to manage
backuping through the restic app.

Classes:
    ResticAdapter: Adapter class for managing backups.
"""

import json
from typing import Dict, List, Union, Optional
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.modules.backup import config
from openvair.libs.cli.models import ExecutionResult
from openvair.modules.tools.utils import change_directory
from openvair.modules.backup.adapters.restic.exceptions import (
    ResticError,
    ResticBackupError,
    ResticRestoreError,
    ResticInitRepoError,
)
from openvair.modules.backup.adapters.restic.return_codes import ReturnCode
from openvair.modules.backup.adapters.restic.restic_executor import (
    ResticCommandExecutor,
)

LOG = get_logger(__name__)


class ResticAdapter:
    """Encapsulates business logic for interacting with restic.

    This class provides methods for initializing repositories, performing
    backups, restoring data, and fetching snapshots, leveraging the
    ResticCommandExecutor to execute commands and validate results.

    Attributes:
        INIT_SUBCOMMAND (str): Subcommand for initializing a repository.
        BACKUP_SUBCOMMAND (str): Subcommand for creating backups.
        RESTORE_SUBCOMMAND (str): Subcommand for restoring data.
        SNAPSHOTS_SUBCOMMAND (str): Subcommand for listing snapshots.
        restic_dir (Path): Path to the restic repository.
        restic_pass (str): Password for the restic repository.
        executor (ResticCommandExecutor): The command executor for restic.
    """

    INIT_SUBCOMMAND = 'init'
    BACKUP_SUBCOMMAND = 'backup --skip-if-unchanged'
    RESTORE_SUBCOMMAND = 'restore --target'
    SNAPSHOTS_SUBCOMMAND = 'snapshots'

    def __init__(self) -> None:
        """Initialize a ResticAdapter instance.

        This initializes the adapter with the repository path and password
        from the configuration, and sets up the ResticCommandExecutor.
        """
        self.restic_dir: Path = config.RESTIC_DIR
        self.restic_pass: str = config.RESTIC_PASSWORD
        self.executor = ResticCommandExecutor(
            str(self.restic_dir),
            self.restic_pass,
        )

    def init_repository(self) -> None:
        """Executes the command to initialize a restic repository.

        Raises:
            ResticInitRepoError: If the repository initialization fails.
        """
        result = self.executor.execute(self.INIT_SUBCOMMAND)

        try:
            self._check_result(
                self.INIT_SUBCOMMAND,
                result,
                ReturnCode.from_code(result.returncode),
            )
        except ResticError as err:
            actual_error = ResticInitRepoError(f'{err!s}')
            LOG.error(actual_error)
            raise actual_error from err

    def backup(self, source_path: Path) -> Dict[str, Union[str, int]]:
        """Performs a backup of the specified source path.

        Args:
            source_path (Path): Path to the directory or files to back up.

        Returns:
            Dict[str, Union[str, int]]: Information about the backup, parsed
                from the JSON output of the restic command.

        Raises:
            ResticBackupError: If the backup operation fails.
        """
        with change_directory(source_path):
            result = self.executor.execute(f'{self.BACKUP_SUBCOMMAND} * ')

        try:
            self._check_result(
                self.BACKUP_SUBCOMMAND,
                result,
                ReturnCode.from_code(result.returncode),
            )
        except ResticError as err:
            actual_error = ResticBackupError(f'{err!s}')
            LOG.error(actual_error)
            raise actual_error from err

        backup_info: Dict[str, Union[str, int]] = json.loads(result.stdout)
        return backup_info

    def snapshots(self) -> List[Dict[str, Union[str, int]]]:
        """Fetches a list of snapshots from the restic repository.

        Returns:
            List[Dict[str, Union[str, int]]]: List of snapshot details, parsed
                from the JSON output of the restic command.
        """
        result = self.executor.execute(self.SNAPSHOTS_SUBCOMMAND)

        self._check_result(
            self.SNAPSHOTS_SUBCOMMAND,
            result,
            ReturnCode.from_code(result.returncode),
        )

        snapshots_info: List[Dict[str, Union[str, int]]] = json.loads(
            result.stdout
        )
        return snapshots_info

    def restore(
        self,
        target_path: Path,
        backup_id: str = 'latest',
    ) -> Dict[str, Union[str, int]]:
        """Restores data from a specified backup.

        Args:
            target_path (Path): Path to restore data to.
            backup_id (str, optional): ID of the backup to restore. Defaults to
                'latest'.

        Returns:
            Dict[str, Union[str, int]]: Information about the restore process,
            parsed from the JSON output of the restic command.

        Raises:
            ResticRestoreError: If the restore operation fails.
        """
        result = self.executor.execute(
            f'{self.RESTORE_SUBCOMMAND} {target_path} {backup_id}'
        )

        try:
            self._check_result(
                self.BACKUP_SUBCOMMAND,
                result,
                ReturnCode.from_code(result.returncode),
            )
        except ResticError as err:
            actual_error = ResticRestoreError(f'{err!s}')
            LOG.error(actual_error)
            raise actual_error from err

        restore_info: Dict[str, Union[str, int]] = json.loads(result.stdout)
        return restore_info

    def _check_result(
        self,
        operation: str,
        result: ExecutionResult,
        return_code: Optional[ReturnCode],
    ) -> None:
        """Checks the result of a restic command and validates its success.

        Args:
            operation (str): The operation being performed (e.g., "backup").
            result (ExecutionResult): The result of the executed command.
            return_code (Optional[ReturnCode]): The return code of the command.

        Raises:
            ResticError: If the command result is unsuccessful or the return
                code indicates failure.
        """
        if return_code is None or return_code != ReturnCode.SUCCESS:
            description = (
                return_code.description if return_code else 'Unknown exit code'
            )
            message = (
                f'Operation {operation} not success '
                f'(exit code: {result.returncode}, description: {description})'
                f'\n\tstderr: {result.stderr}'
            )
            error = ResticError(message)
            raise error
