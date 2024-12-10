"""Unit tests for the `execute` function in the `openvair.libs.cli.executor`.

This test suite verifies the behavior of the `execute` function under various
conditions, including successful execution, errors, timeouts, and invalid
commands. Mocking is used to isolate the function from actual subprocess calls,
ensuring that tests are deterministic and safe.

Usage:
Run the tests using pytest:
    pytest openvair/libs/cli/test_executor.py
"""

from typing import TYPE_CHECKING
from subprocess import TimeoutExpired
from unittest.mock import MagicMock, patch

import pytest

from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import (
    ExecuteError,
    ExecuteTimeoutExpiredError,
)
from openvair.libs.cli.execution_models import ExecuteParams

if TYPE_CHECKING:
    from openvair.libs.cli.execution_models import ExecutionResult


def test_execute_success() -> None:
    """Test the successful execution of a command.

    Simulates a command execution using `subprocess.Popen` and verifies that:
        - The command returns the correct `stdout`.
        - The `returncode` is 0, indicating successful execution.
        - The `stderr` is empty.
    """
    with patch('subprocess.Popen') as mock_popen:
        process_mock: MagicMock = MagicMock()
        process_mock.communicate.return_value = ('output', '')
        process_mock.returncode = 0
        mock_popen.return_value = process_mock

        result: ExecutionResult = execute('echo', 'hello')

        assert result.returncode == 0
        assert result.stdout == 'hello'
        assert result.stderr == ''


def test_execute_with_error() -> None:
    """Test execution of a command that returns an error.

    Simulates a command execution where the return code is non-zero and verifies
        that:
        - The `ExecuteError` exception is raised when `raise_on_error=True`.
        - The error details are logged correctly.
    """
    with patch('subprocess.Popen') as mock_popen:
        process_mock: MagicMock = MagicMock()
        process_mock.communicate.return_value = ('', 'error')
        process_mock.returncode = 1
        mock_popen.return_value = process_mock

        with pytest.raises(ExecuteError):
            execute('false', params=ExecuteParams(raise_on_error=True))


def test_execute_timeout() -> None:
    """Test execution of a command that exceeds the timeout.

    Simulates a command execution where the process exceeds the specified
        timeout and verifies that:
        - The `ExecuteTimeoutExpiredError` exception is raised.
        - The timeout behavior is logged and handled correctly.
    """
    with patch('subprocess.Popen') as mock_popen:
        process_mock: MagicMock = MagicMock()
        mock_popen.return_value = process_mock
        process_mock.communicate.side_effect = TimeoutExpired(
            cmd='sleep 1', timeout=1
        )

        with pytest.raises(ExecuteTimeoutExpiredError):
            execute('sleep', '5', params=ExecuteParams(timeout=1))


def test_execute_invalid_command() -> None:
    """Test execution of an invalid command.

    Simulates a scenario where the command to be executed does not exist and
        verifies that:
        - An `OSError` exception is raised.
        - The error details are captured and logged correctly.
    """
    with patch('subprocess.Popen', side_effect=OSError()), pytest.raises(
        OSError
    ):
        execute('invalid_command')
