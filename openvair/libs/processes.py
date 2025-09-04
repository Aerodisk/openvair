"""Utilities for interacting with system processes via CLI.

This module provides helper functions for locating and inspecting system
processes, particularly for identifying processes by network port using `lsof`.
It wraps CLI interaction with structured exception handling and logging.

Classes:
    ProcessNotFoundError: Custom exception for missing processes.

Functions:
    find_process_by_port: Return process ID listening on a given TCP port.

Attributes:
    LOG: Module-level logger instance.
"""

from typing import Any

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.abstracts.base_exception import BaseCustomException

LOG = get_logger(__name__)


class ProcessNotFoundError(BaseCustomException):
    """Raised when no process is found listening on the specified port."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with the given arguments.

        Args:
            message (str): The error message describing the issue.
            *args (Any): Additional arguments for exception initialization.
        """
        super().__init__(message, *args)


def find_process_by_port(port: int) -> int:
    """Find the PID of the process listening on the specified TCP port.

    This function uses the `lsof` command-line tool to identify the process
    ID (PID) of a process currently bound to the given TCP port. It performs
    structured logging and raises custom exceptions in case of failure.

    Args:
        port (int): TCP port number to check.

    Returns:
        int: PID of the process listening on the specified port.

    Raises:
        ExecuteError: If the CLI command `lsof` fails to execute.
        ProcessNotFoundError: If the output is malformed or no process is found.
    """
    try:
        result = execute(
            'lsof',
            '-ti',
            f':{port}',
            params=ExecuteParams(timeout=10.0, raise_on_error=True),
        )
    except ExecuteError as err:
        LOG.error(err)
        raise

    proc_id = None
    if result.returncode == 0 and result.stdout.strip():
        try:
            proc_id = int(result.stdout.strip().split('\n')[0])
        except ValueError as err:
            message = 'Error while parsing output of getting processes'
            LOG.error(message)
            raise ProcessNotFoundError(message) from err

    if not proc_id:
        msg = f'Failed to find websockify PID for port {port}'
        LOG.error(msg)
        raise ProcessNotFoundError(msg)
    return proc_id
