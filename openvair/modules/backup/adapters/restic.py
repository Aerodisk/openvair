"""Adapter for interacting with restic by executing bash command.

This module provides the `ResticAdapter` class, which is used to manage
backuping through the restic app.

Classes:
    ResticAdapter: Adapter class for managing backups.
"""

from pathlib import Path

from openvair.modules.tools import utils
from openvair.modules.backup.adapters.exceptions import ResticAdapterException


class ResticAdapter:
    """Provides interaction with restic via the CLI"""

    COMMAND_FORMAT = 'sudo restic --json'

    def __init__(self, repo_path: Path) -> None:
        """Initialize ResticAdapter instance

        Args:
            repo_path (Path): path to restic repository
        """
        self.repo_path = repo_path

    def _build_full_command(self, subcommand: str) -> str:
        return f'{self.COMMAND_FORMAT} {subcommand}'

    def _execute_command(self, command: str) -> str:
        stdout, stderr = utils.execute(command)
        if stderr:
            message = f'Error response from command: {command}'
            raise ResticAdapterException(message)
        return stdout

    def repo_exist(self) -> bool:
        """Checks restic repository existance"""
        subcommand = (
            f'check -r {self.repo_path} --password-file /tmp/restic_pass'
        )
        command = self._build_full_command(subcommand)
        try:
            # TODO, логика проверки, существует репозиторий или же например имеет ошибки
            self._execute_command(command)
        except ResticAdapterException:
            return False
        else:
            return True
