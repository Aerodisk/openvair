"""Custom exceptions for the adapters of storage module.

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

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class PartedError(BaseCustomException):
    """Raised when an error during partition operations using the `parted"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize PartedError with optional arguments."""
        super().__init__(message, *args)
