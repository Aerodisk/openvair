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

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NfsPathDoesNotExistOnShareError(BaseCustomException):
    """Raised when the specified NFS path does not exist on the share."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NfsPathDoesNotExistOnShareError."""
        super().__init__(message, *args)


class NfsIpIsNotAvailableError(BaseCustomException):
    """Raised when the specified NFS IP address is not available."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NfsIpIsNotAvailableError with optional arguments."""
        super().__init__(message, *args)


class GettinStorageInfoError(BaseCustomException):
    """Raised when an error occurs while retrieving storage information."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize GettinStorageInfoError with optional arguments."""
        super().__init__(message, *args)


class NFSCantBeMountError(BaseCustomException):
    """Raised when an NFS share cannot be mounted."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NFSCantBeMountError with optional arguments."""
        super().__init__(message, *args)


class PackageIsNotInstalled(BaseCustomException):
    """Exception raised when a required package is not installed on the system.

    This exception is used to indicate that a necessary software package is
    missing, which is required for the execution of a specific operation.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the PackageIsNotInstalled with the provided arguments."""
        super().__init__(message, *args)
