"""Module to execute and manage qemu-img commands.

Provides a structured interface to run `qemu-img` commands and process their
results, with logging and optional environment control.

Dependencies:
    - openvair.libs.log
    - openvair.libs.cli.models (ExecuteParams, ExecutionResult)
    - openvair.libs.cli.executor (execute)
"""

from typing import Optional

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams, ExecutionResult
from openvair.libs.cli.executor import execute

LOG = get_logger(__name__)


class QemuImgCommandExecutor:
    """Executes qemu-img commands and handles output/errors.

    Supports generic execution of qemu-img commands like:
    - info
    - convert
    - create
    - check
    """

    BASE_COMMAND = 'qemu-img'

    def __init__(self) -> None:
        """Initialize the QemuImgCommandExecutor."""
        ...

    def _build_command(self, subcommand: str) -> str:
        """Constructs the full qemu-img command.

        Args:
            subcommand (str): The qemu-img subcommand and arguments.

        Returns:
            str: Full shell command.
        """
        return f'{self.BASE_COMMAND} {subcommand}'

    def execute(
        self,
        subcommand: str,
        timeout: Optional[float] = None,
    ) -> ExecutionResult:
        """Executes the qemu-img command with optional timeout.

        Args:
            subcommand (str): Subcommand and arguments (e.g. 'info /path').
            timeout (Optional[float]): Timeout in seconds.

        Returns:
            ExecutionResult: The result of the command execution.
        """
        command = self._build_command(subcommand)
        LOG.debug(f'Executing qemu-img command: {command}')
        result: ExecutionResult = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                timeout=timeout,
                shell=True,
                root_helper='sudo -E',
            ),
        )
        return result
