"""Custom exceptions for the adapters of storage module.

This module defines custom exceptions used in the storage adapters
for handling errors related to storages  operations.

"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class PartedError(BaseCustomException):
    """Raised when an error during partition operations using the `parted"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize PartedError with optional arguments."""
        super().__init__(message, *args)
