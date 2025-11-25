"""Module for custom exceptions in the physical filesystem storage domain.

This module defines custom exceptions that are used within the physical
filesystem storage domain. These exceptions extend the `BaseCustomException`
class from the `tools` module and are used to handle specific error cases
involving physical filesystem operations.

Classes:
    UnmountError: Raised when an error occurs during the unmounting process.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class UnmountError(BaseCustomException):
    """Raised when an error occurs during the unmounting process."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize UnmountError with optional arguments."""
        super().__init__(message, *args)
