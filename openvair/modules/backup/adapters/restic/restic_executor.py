from enum import Enum
from typing import NoReturn, Optional

from typing_extensions import Self

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams, ExecutionResult
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import (
    ExecuteError,
    ExecuteTimeoutExpiredError,
)
from openvair.abstracts.base_exception import BaseCustomException
from openvair.modules.backup.adapters.restic.exceptions import (
    ResticExecutorError,
)
from openvair.modules.backup.adapters.restic.return_codes import ReturnCode

LOG = get_logger(__name__)


class ResticCommandExecutor:
    """Executes restic commands and handles errors."""

    COMMAND_FORMAT = 'restic --json'

    def __init__(self, restic_dir: str, restic_pass: str) -> None:
        """Initialize the executor with the repository path.

        Args:
            restic_dir (str): Path to the restic repository.
            restic_pass (str): Password for the restic repository.
        """
        self.restic_dir = str(restic_dir)
        self.restic_pass = restic_pass

    def init_repository(self) -> ExecutionResult:
        command = self._build_command('init')
        return self._execute(command)

    def _build_command(self, subcommand: str) -> str:
        """Build the full restic command with necessary options.

        Args:
            subcommand (str): The subcommand to execute with restic.

        Returns:
            str: The complete command string.
        """
        return f'{self.COMMAND_FORMAT} -r {self.restic_dir} {subcommand}'

    def _execute(
        self, command: str, timeout: Optional[float] = None
    ) -> ExecutionResult:
        """Executes a command and checks the result.

        Args:
            command (str): The command to execute.
            timeout (float): Timeout for the command.

        Returns:
            ExecutionResult: The result of the command execution.

        Raises:
            ResticAdapterException: If the command fails or encounters an error.
        """
        try:
            LOG.debug(f'Executing command: {command}')
            result: ExecutionResult = execute(
                command,
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    timeout=timeout,
                    shell=True,
                    root_helper='sudo -E',
                    env={
                        'RESTIC_PASSWORD': self.restic_pass,
                        'RESTIC_REPOSITORY': self.restic_dir,
                    },
                ),
            )
            self._check_result(command, result)
        except (ExecuteTimeoutExpiredError, ExecuteError, OSError) as e:
            self._handle_error(command, e)
        else:
            return result

    def _check_result(self, command: str, result: ExecutionResult) -> None:
        """Checks the result and raises an exception if it fails.

        Args:
            command (str): The executed command.
            result: The result object returned by the execute function.

        Raises:
            ResticAdapterException: If the command failed.
        """
        return_code = ReturnCode.from_code(result.returncode)
        if return_code is None or return_code != ReturnCode.SUCCESS:
            LOG.error(
                f"Command '{command}' failed with return code "
                f'{result.returncode}. Stderr: {result.stderr}'
            )
            description = (
                return_code.description if return_code else 'Unknown exit code'
            )
            msg = (
                f'Command failed: {result.stderr} '
                f'(exit code: {result.returncode}, description: {description})'
            )
            raise ResticExecutorError(msg)

    def _handle_error(self, command: str, exception: Exception) -> NoReturn:
        """Handles errors raised during command execution.

        Args:
            command (str): The executed command.
            exception (Exception): The raised exception.

        Raises:
            ResticExecutorException: Wrapped exception with additional context.
        """
        error_mapping = {
            ExecuteTimeoutExpiredError: (
                "Command '{command}' timed out: {exception!s}"
            ),
            ExecuteError: (
                "Command execution error for '{command}': {exception!s}"
            ),
            OSError: "OS error while executing '{command}': {exception!s}",
        }

        for exc_type, message_template in error_mapping.items():
            if isinstance(exception, exc_type):
                LOG.error(
                    message_template.format(
                        command=command, exception=exception
                    )
                )
                raise ResticExecutorError(
                    message_template.format(
                        command=command, exception=exception
                    )
                ) from exception

        # Default case for unexpected errors
        LOG.error(f"Unexpected error for command '{command}': {exception!s}")
        msg = f'Unexpected error: {exception!s}'
        raise ResticExecutorError(msg) from exception
