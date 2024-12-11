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
from openvair.modules.backup.adapters.exceptions import (
    ResticExecutorException,
)

LOG = get_logger(__name__)


class ReturnCode(Enum):
    """Represents exit codes for commands and their descriptions.

    This Enum maps numerical exit codes to their corresponding textual
    descriptions. These exit codes are used to determine the result of
    executed commands and to provide meaningful error messages.
    """

    SUCCESS = 0, 'Command was successful'
    COMMAND_FAILED = 1, 'Command failed, see command help for more details'
    GO_RUNTIME_ERROR = 2, 'Go runtime error'
    PARTIAL_BACKUP = 3, 'Backup command could not read some source data'
    REPO_NOT_EXIST = 10, 'Repository does not exist (since restic 0.17.0)'
    REPO_LOCK_FAILED = 11, 'Failed to lock repository (since restic 0.17.0)'
    WRONG_PASSWORD = 12, 'Wrong password (since restic 0.17.1)'
    INTERRUPTED = 130, 'Restic was interrupted using SIGINT or SIGSTOP'

    def __init__(self, code: int, description: str) -> None:
        """Initializes a ReturnCode instance with a code and description.

        Args:
            code (int): The numerical exit code associated with the command.
            description (str): A textual description of the exit code.
        """
        self.code: int = code
        self.description: str = description

    @classmethod
    def from_code(cls, code: int) -> Optional[Self]:
        """Finds the corresponding ReturnCode by numerical exit code.

        Args:
            code (int): The numerical exit code to look up.

        Returns:
            Optional[Self]: The matching ReturnCode instance if found, or None
            if the code does not correspond to a defined ReturnCode.
        """
        return next((rc for rc in cls if rc.code == code), None)


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
        result = self._execute(command)
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
        self, command: str, timeout: Optional[float] = 60.0
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
            # msg = (
            #     f'Command failed: {result.stderr} '
            #     f'(exit code: {result.returncode}, description: {description})'
            # )
            # raise ResticExecutorException(msg)

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
                raise ResticExecutorException(
                    message_template.format(
                        command=command, exception=exception
                    )
                ) from exception

        # Default case for unexpected errors
        LOG.error(f"Unexpected error for command '{command}': {exception!s}")
        msg = f'Unexpected error: {exception!s}'
        raise ResticExecutorException(msg) from exception
