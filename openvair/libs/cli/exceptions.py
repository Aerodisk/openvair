"""Defines custom exceptions for handling errors during command execution.

Classes:
    ExecuteTimeoutExpiredError: Raised when a command execution exceeds the
        specified timeout.
    ExecuteError: General exception for command execution errors.

Dependencies:
    openvair.abstracts.base_exception: Provides the BaseCustomException class
        for creating custom exceptions.
"""

from typing import Any, Optional

from openvair.abstracts.base_exception import BaseCustomException


class ExecuteTimeoutExpiredError(BaseCustomException):
    """Raised when a command execution reaches its timeout."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ExecuteTimeoutExpiredError."""
        super().__init__(message, *args)


class ExecuteError(Exception):
    """General exception for command execution errors."""

    def __init__(self, message: Optional[str] = None):
        """Initialize the ExecuteError.

        Args:
            message (Optional[str]): An optional error message to provide
                context for the exception.
        """
        super(ExecuteError, self).__init__(message)
