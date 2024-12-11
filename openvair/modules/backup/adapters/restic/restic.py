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
    ResticInitRepoError,
    ResticBackupRepoError,
)
from openvair.modules.backup.adapters.restic.return_codes import ReturnCode
from openvair.modules.backup.adapters.restic.restic_executor import (
    ResticCommandExecutor,
)

LOG = get_logger(__name__)


class ResticAdapter:
    """Provides business logic for interacting with restic."""

    INIT_SUBCOMMAND = 'init'
    BACKUP_SUBCOMMAND = 'backup --skip-if-unchanged'
    SNAPSHOTS_SUBCOMMAND = 'snapshots'

    def __init__(self) -> None:
        """Initialize ResticAdapter instance."""
        self.restic_dir: Path = config.RESTIC_DIR
        self.restic_pass: str = config.RESTIC_PASSWORD
        self.executor = ResticCommandExecutor(
            str(self.restic_dir),
            self.restic_pass,
        )

    def init_repository(self) -> None:
        """Executes command to init restic repository"""
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
        with change_directory(source_path):
            result = self.executor.execute(f'{self.BACKUP_SUBCOMMAND} * ')

        try:
            self._check_result(
                self.BACKUP_SUBCOMMAND,
                result,
                ReturnCode.from_code(result.returncode),
            )
        except ResticError as err:
            actual_error = ResticBackupRepoError(f'{err!s}')
            LOG.error(actual_error)
            raise actual_error from err

        backup_info: Dict[str, Union[str, int]] = json.loads(result.stdout)
        return backup_info

    def snapshots(self) -> List[Dict[str, Union[str, int]]]:
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

    def _check_result(
        self,
        operation: str,
        result: ExecutionResult,
        return_code: Optional[ReturnCode],
    ) -> None:
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


if __name__ == '__main__':
    r = ResticAdapter()
    # res = r.backup(Path('/opt/aero/openvair/data'))
    r.snapshots()
