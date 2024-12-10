"""Executor module for running shell commands with advanced error handling.

Functions:
    __terminate_process: Attempts to gracefully terminate a subprocess and
        forcefully kills it if necessary.
    __prepare_env: Prepares the environment variables for command execution.
    execute: Executes a shell command with optional root privileges,
        timeout, and error handling.
"""

import os
from typing import Dict, List
from subprocess import PIPE, Popen, TimeoutExpired

from openvair.libs.cli.models import ExecuteParams, ExecutionResult
from openvair.libs.cli.exceptions import (
    ExecuteError,
    ExecuteTimeoutExpiredError,
)
from openvair.modules.tools.utils import LOG


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


def __prepare_env(env_params: Dict[str, str]) -> Dict[str, str]:
    """Prepares the environment variables for the command execution.

    Args:
        env_params (Dict[str, str]): Key-value pairs representing environment
            variables to be added or overridden.

    Returns:
        Dict[str, str]: The merged environment variables, combining the current
        environment and the provided `env_params`.
    """
    env_vars = os.environ.copy()  # Copy current environment
    for var, val in env_params.items():
        env_vars[var] = val
    return env_vars


def execute(
    *args: str,
    params: ExecuteParams = ExecuteParams(),
) -> ExecutionResult:
    """Executes a shell command and returns its stdout, stderr, and exit code.

    Args:
        *args (str): The command and its arguments to execute. Each argument
            must be passed as a separate string.
        params (ExecuteParams): A Pydantic model containing command execution
            parameters such as `shell`, `timeout`, `env`, etc.

    Returns:
        ExecutionResult: A model containing:
            - `returncode` (int): The exit code of the command.
            - `stdout` (str): Standard output of the command.
            - `stderr` (str): Standard error output of the command.

    Raises:
        ExecuteTimeoutExpiredError: Raised if the command execution exceeds the
            specified timeout.
        ExecuteError: Raised if the command exits with a non-zero return code
            and `raise_on_error` is True.
        OSError: Raised for system-level errors, such as command not found or
            permission issues.

    Example:
        >>> params = ExecuteParams(shell=True, timeout=10, raise_on_error=True)
        >>> result = execute('ls', '-la', params=params)
        >>> print(result.stdout)
    """
    cmd: List[str] = list(args)
    if params.run_as_root and hasattr(os, 'geteuid') and os.geteuid() != 0:
        cmd = [params.root_helper, *cmd]

    cmd_str = ' '.join(cmd)
    LOG.info(f'Executing command: {cmd_str}')
    try:
        with Popen(  # noqa: S603
            cmd_str if params.shell else cmd,
            shell=params.shell,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            text=True,
            env=__prepare_env(params.env) if params.env else None,
        ) as proc:
            try:
                stdout, stderr = proc.communicate(timeout=params.timeout)
                returncode = proc.returncode
                LOG.info(
                    f"Command '{cmd_str}' completed with return code: "
                    f'{returncode}'
                )

                if params.raise_on_error and returncode != 0:
                    message = (
                        f"Command '{cmd_str}' failed with return code "
                        f'{returncode}'
                    )
                    LOG.error(message)
                    raise ExecuteError(message)

                return ExecutionResult(
                    returncode=returncode,
                    stdout=stdout.strip() or '',
                    stderr=stderr.strip() or '',
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
