"""Module for custom exceptions in the remote filesystem storage domain.

This module defines custom exceptions that are used within the remote
filesystem storage domain. These exceptions extend the `BaseCustomException`
class from the `tools` module and are used to handle specific error cases
involving remote filesystem operations.

Classes:
    NfsPathDoesNotExistOnShareError: Raised when the specified NFS path
        does not exist on the share.
    NfsIpIsNotAvailableError: Raised when the specified NFS IP address
        is not available.
    GettinStorageInfoError: Raised when an error occurs while retrieving
        storage information.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class NfsPathDoesNotExistOnShareError(BaseCustomException):
    """Raised when the specified NFS path does not exist on the share."""

    def __init__(self, *args):
        """Initialize NfsPathDoesNotExistOnShareError with optional arguments.

        Args:
            *args: Variable length argument list for exception details.
        """
        super().__init__(*args)


class NfsIpIsNotAvailableError(BaseCustomException):
    """Raised when the specified NFS IP address is not available."""

    def __init__(self, *args):
        """Initialize NfsIpIsNotAvailableError with optional arguments.

        Args:
            *args: Variable length argument list for exception details.
        """
        super().__init__(*args)


class GettinStorageInfoError(BaseCustomException):
    """Raised when an error occurs while retrieving storage information."""

    def __init__(self, *args):
        """Initialize GettinStorageInfoError with optional arguments.

        Args:
            *args: Variable length argument list for exception details.
        """
        super().__init__(*args)


class NFSCantBeMountError(BaseCustomException):
    """Raised when an NFS share cannot be mounted."""

    def __init__(self, *args):
        """Initialize NFSCantBeMountError with optional arguments.

        Args:
            *args: Variable length argument list for exception details.
        """
        super().__init__(*args)


class PackageIsNotInstalled(BaseCustomException):
    """Exception raised when a required package is not installed on the system.

    This exception is used to indicate that a necessary software package is
    missing, which is required for the execution of a specific operation.

    Attributes:
        args: Arguments passed to the exception, typically including the name of
            the missing package.
    """

    def __init__(self, *args):
        """Initialize the PackageIsNotInstalled with the provided arguments.

        Args:
            args: Variable length argument list to pass error details, typically
                the name of the missing package.
        """
        super().__init__(*args)
