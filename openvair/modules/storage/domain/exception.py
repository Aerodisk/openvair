"""Module for custom exceptions related to storage domain operations.

This module defines custom exceptions that are specific to the storage domain,
providing more context and control over error handling in storage-related
operations.

Classes:
    WrongPartitionRangeError: Exception raised when a partition range is
        incorrect.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class WrongPartitionRangeError(BaseCustomException):
    """Exception raised when the specified partition range is incorrect.

    This exception is intended to be used when a partition operation fails due
    to an invalid or unsupported partition range.
    """

    def __init__(self, *args):
        """Initialize the WrongPartitionRangeError with the provided arguments.

        Args:
            args: Variable length argument list to pass error details.
        """
        super().__init__(*args)

class UnsupportedPartitionTableTypeError(BaseCustomException):
    """Exception raised when an unsupported partition table type is encountered.

    This exception is intended to be used when a partition operation fails due
    to an unrecognized or unsupported partition table type.
    """

    def __init__(self, *args):
        """Initialize the UnsupportedPartitionTableTypeError.

        Args:
            args: Variable length argument list to pass error details.
        """
        super().__init__(*args)
