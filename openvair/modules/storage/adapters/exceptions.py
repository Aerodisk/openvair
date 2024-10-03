"""Module for custom exceptions in the storage adapters layer.

This module defines custom exceptions that are used within the storage
adapters layer. These exceptions extend either `BaseCustomException` from
the `tools` module or Python's built-in `Exception` class, and are used to
handle specific error cases in the storage operations.

Classes:
    DBCannotBeConnectedError: Raised when a connection to the database
        cannot be established.
    PartedError: Raised when an error occurs during partition operations
        using the `parted` utility.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class DBCannotBeConnectedError(Exception):
    """Raised when a connection to the database cannot be established."""

    def __init__(self, message: str):
        """Initialize DBCannotBeConnectedError with a specific error message.

        Args:
            message (str): The error message to be displayed.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self):
        """Return the error message as a string."""
        return self.message


class PartedError(BaseCustomException):
    """Raised when an error during partition operations using the `parted"""

    def __init__(self, *args):
        """Initialize PartedError with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super(PartedError, self).__init__(*args)
