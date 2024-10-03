"""Exception classes for virtual network operations in the service layer.

This module defines custom exceptions related to virtual network operations,
which are used throughout the service layer.

Classes:
    - DataBaseVirtualNetworkException: Raised when a database-related error
        occurs in virtual network operations.
    - VirtualNetworkAlreadyExist: Raised when a virtual network already exists
        and cannot be created.
    - VirtualNetworkDoesNotExist: Raised when a requested virtual network does
        not exist.
    - PortGroupException: Raised when an error occurs related to port groups in
        a virtual network.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class DataBaseVirtualNetworkException(BaseCustomException):
    """Raised when a database error occurs in virtual network operations."""
    def __init__(self, *args):
        """Initialize the exception with optional arguments.

        Args:
            *args: Variable length argument list for the exception.
        """
        super().__init__(*args)


class VirtualNetworkAlreadyExist(BaseCustomException):
    """Raised when a virtual network already exists and cannot be created."""

    def __init__(self, *args):
        """Initialize the exception with optional arguments.

        Args:
            *args: Variable length argument list for the exception.
        """
        super().__init__(*args)


class VirtualNetworkDoesNotExist(BaseCustomException):
    """Raised when a requested virtual network does not exist."""

    def __init__(self, *args):
        """Initialize the exception with optional arguments.

        Args:
            *args: Variable length argument list for the exception.
        """
        super().__init__(*args)


class PortGroupException(BaseCustomException):
    """Raised when an error occurs related to port groups in virtual network."""

    def __init__(self, *args):
        """Initialize the exception with optional arguments.

        Args:
            *args: Variable length argument list for the exception.
        """
        super().__init__(*args)
