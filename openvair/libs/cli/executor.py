"""Executor module for running shell commands with advanced error handling.

Functions:
    terminate_process: Attempts to gracefully terminate a subprocess and
        forcefully kills it if necessary.
    __run_command: Executes a subprocess, handles timeout and errors, and
        returns the results.
    execute: Executes a shell command with optional root privileges,
        timeout, and error handling.
"""

import os
from typing import List, Optional
from subprocess import PIPE, Popen, TimeoutExpired

from openvair.libs.cli.exceptions import (
    ExecuteError,
    ExecuteTimeoutExpiredError,
)
from openvair.modules.tools.utils import LOG
from openvair.libs.cli.execution_models import ExecutionResult


def __terminate_process(proc: Popen, cmd_str: str) -> str:
    """Terminates a subprocess gracefully, kills it if termination fails.

    Attempts to gracefully terminate a subprocess and forcefully kill it
    if termination fails.

    Args:
        proc (Popen): The subprocess to be terminated.
        cmd_str (str): The command string representing the subprocess for
            logging purposes.

    Returns:
        str: The standard error output (stderr) collected from the subprocess
            after termination.
    """
    LOG.warning(f"Command '{cmd_str}' timed out. Terminating process.")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except TimeoutExpired:
        LOG.error(f"Command '{cmd_str}' did not terminate. Killing it.")
        proc.kill()
    _, stderr = proc.communicate()
    return str(stderr)

def execute(
    *args: str,
    shell: bool = False,
    run_as_root: bool = False,
    root_helper: str = 'sudo',
    timeout: Optional[float] = None,
    raise_on_error: bool = False,
) -> ExecutionResult:
    """Executes a shell command and returns its stdout, stderr, and exit code.

    Args:
        *args (str): The command and its arguments to execute. Each argument
            must be passed as a separate string.
        shell (bool): If True, the command will be executed through the shell.
            Defaults to False.
        run_as_root (bool): If True, the command will be executed with root
            privileges using the specified root_helper. Defaults to False.
        root_helper (str): The command used to elevate privileges, such as
            'sudo'. Defaults to 'sudo'.
        timeout (Optional[float]): Maximum time in seconds to wait for the
            command to complete. Defaults to None (no timeout).
        raise_on_error (bool): If True, raises an exception if the command exits
            with a non-zero return code. If False, includes the return code
            in the output dictionary for manual handling. Defaults to False.

    Returns:
        Dict[str, Union[str, int]]: A dictionary containing the following keys:
            - 'stdout': Standard output of the command (str).
            - 'stderr': Standard error output of the command (str).
            - 'returncode': The exit code of the command (int). This is included
                only if raise_on_error is False.

    Raises:
        ExecuteTimeoutExpiredError: Raised if the command execution exceeds the
            specified timeout.
        ExecuteError: Raised if the command exits with a non-zero return code
            and raise_on_error is True.
        OSError: Raised for system-level errors, such as command not found or
            permission issues.

    Example:
        >>> execute2('ls', '-l', raise_on_error=True)
        {'stdout': 'output', 'stderr': '', 'returncode': 0}

        >>> execute2('false', raise_on_error=True)
        Traceback (most recent call last):
            ...
        ExecuteError: Command 'false' failed

        >>> result = execute2('false', raise_on_error=False)
        >>> print(result)
        {'stdout': '', 'stderr': '', 'returncode': 1}
    """
    cmd: List[str] = list(args)
    if run_as_root and hasattr(os, 'geteuid') and os.geteuid() != 0:
        cmd = [root_helper, *cmd]

    cmd_str = ' '.join(cmd)
    LOG.info(f'Executing command: {cmd_str}')
    try:
        with Popen(  # noqa: S603
            cmd_str if shell else cmd,
            shell=shell,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            text=True,
        ) as proc:
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                returncode = proc.returncode
                LOG.info(
                    f"Command '{cmd_str}' completed with return code: "
                    f'{returncode}'
                )

                if raise_on_error and returncode != 0:
                    message = (
                        f"Command '{cmd_str}' failed with return code "
                        f'{returncode}'
                    )
                    LOG.error(message)
                    raise ExecuteError(message)

                return ExecutionResult(
                    returncode=returncode,
                    stdout=stdout or '',
                    stderr=stderr or '',
                )
            except TimeoutExpired:
                stderr = __terminate_process(proc, cmd_str)
                message = (
                    f"Command '{cmd_str}' timed out and was killed.\n"
                    f'Error: {stderr}'
                )
                raise ExecuteTimeoutExpiredError(message)
    except OSError as err:
        LOG.error(f"OS error for command '{cmd_str}': {err}")
        raise
