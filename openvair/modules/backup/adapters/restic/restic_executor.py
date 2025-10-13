"""Module to execute and manage restic commands.

This module provides a class for building and executing restic commands
while handling errors. It includes logging, command formatting, and result
validation functionalities.

Dependencies:
    - openvair.libs.log: For logging command execution.
    - openvair.libs.cli.models: For execution parameters and results.
    - openvair.libs.cli.executor: For command execution logic.

Typical usage example:
    executor = ResticCommandExecutor('/path/to/repo', 'password')
    result = executor.execute('backup /path/to/files')
"""


from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams, ExecutionResult
from openvair.libs.cli.executor import execute

LOG = get_logger(__name__)


class ResticCommandExecutor:
    """Executes restic commands and handles errors.

    This class is responsible for constructing and executing restic commands
    with specified parameters. It ensures commands are properly formatted and
    securely executed, leveraging environment variables for authentication.

    Attributes:
        COMMAND_FORMAT (str): The base command format for restic execution.
        restic_dir (str): Path to the restic repository.
        restic_pass (str): Password for the restic repository.
    """

    COMMAND_FORMAT = 'restic --json -q'

    def __init__(self, restic_dir: str, restic_pass: str) -> None:
        """Initialize the executor with the repository path.

        Args:
            restic_dir (str): Path to the restic repository.
            restic_pass (str): Password for the restic repository.
        """
        self.restic_dir = str(restic_dir)
        self.restic_pass = restic_pass

    def _build_command(self, subcommand: str) -> str:
        """Build the full restic command with necessary options.

        Args:
            subcommand (str): The subcommand to execute with restic.

        Returns:
            str: The complete command string.
        """
        return f'{self.COMMAND_FORMAT} -r {self.restic_dir} {subcommand}'

    def execute(
        self, subcommand: str, timeout: float | None = None
    ) -> ExecutionResult:
        """Executes a command and checks the result.

        Args:
            subcommand (str): Subcommand to execute with restic.
            timeout (Optional[float]): Timeout for the command, in seconds.

        Returns:
            ExecutionResult: The result of the command execution.

        Raises:
            ResticAdapterException: If the command fails or encounters an error.
        """
        command = self._build_command(subcommand)
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
        return result
