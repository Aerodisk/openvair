"""Module for custom exceptions related to storage domain operations.

This module defines custom exceptions that are specific to the storage domain,
providing more context and control over error handling in storage-related
operations.

Classes:
    WrongPartitionRangeError: Exception raised when a partition range is
        incorrect.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class WrongPartitionRangeError(BaseCustomException):
    """Exception raised when the specified partition range is incorrect.

    This exception is intended to be used when a partition operation fails due
    to an invalid or unsupported partition range.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the WrongPartitionRangeError"""
        super().__init__(message, *args)


class UnsupportedPartitionTableTypeError(BaseCustomException):
    """Exception raised when an unsupported partition table type is encountered.

    This exception is intended to be used when a partition operation fails due
    to an unrecognized or unsupported partition table type.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UnsupportedPartitionTableTypeError."""
        super().__init__(message, *args)


class PartitionTableInfoNotFound(BaseCustomException):
    """Exception raised when an partition table not foun in parted output."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UnsupportedPartitionTableTypeError."""
        super().__init__(message, *args)


class NotFoundDataInPartitonInfoException(BaseCustomException):
    """Exception raised when not found partition data in partition table info"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UnsupportedPartitionTableTypeError."""
        super().__init__(message, *args)
