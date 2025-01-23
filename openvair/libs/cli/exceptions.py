"""Defines custom exceptions for handling errors during command execution.

Classes:
    ExecuteTimeoutExpiredError: Raised when a command execution exceeds the
        specified timeout.
    ExecuteError: General exception for command execution errors.

Dependencies:
    openvair.abstracts.base_exception: Provides the BaseCustomException class
        for creating custom exceptions.
"""

from openvair.abstracts.base_exception import BaseCustomException


class ExecuteError(BaseCustomException):
    """General exception for command execution errors."""

    ...


class ExecuteTimeoutExpiredError(ExecuteError):
    """Raised when a command execution reaches its timeout."""

    ...


class UnsuccessReturnCodeError(ExecuteError):
    """Raised when getting unsuccesses return code"""

    ...
