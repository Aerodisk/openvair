"""Module for custom exceptions in the physical filesystem storage domain.

This module defines custom exceptions that are used within the physical
filesystem storage domain. These exceptions extend the `BaseCustomException`
class from the `tools` module and are used to handle specific error cases
involving physical filesystem operations.

Classes:
    UnmountError: Raised when an error occurs during the unmounting process.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class UnmountError(BaseCustomException):
    """Raised when an error occurs during the unmounting process."""

    def __init__(self, *args):
        """Initialize UnmountError with optional arguments.

        Args:
            *args: Variable length argument list for exception details.
        """
        super().__init__(*args)
