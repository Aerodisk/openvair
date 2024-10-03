"""Custom exceptions for the network service layer.

This module defines custom exceptions used in the network service layer
for handling errors related to network interface and bridge operations.

Classes:
    InterfaceNotFoundError: Raised when a network interface is not found.
    BridgeNameExistException: Raised when a bridge name already exists.
    BridgeNameDoesNotExistException: Raised when a bridge name does not exist.
    UnexpectedDataArguments: Raised when unexpected data arguments are provided.
    InterfaceInsertionError: Raised when an error occurs during interface
        insertion.
    CreateInterfaceDataException: Raised when there is an error creating
        interface data.
    InterfaceDeletingError: Raised when an error occurs during interface
        deletion.
    NetplanApplyException: Raised when an error occurs applying a Netplan
        configuration.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class InterfaceNotFoundError(BaseCustomException):
    """Exception raised when a network interface is not found."""

    def __init__(self, *args):
        """Initialize InterfaceNotFoundError with optional arguments."""
        super().__init__(*args)


class BridgeNameExistException(BaseCustomException):
    """Exception raised when a bridge name already exists."""

    def __init__(self, *args):
        """Initialize BridgeNameExistException with optional arguments."""
        super().__init__(*args)


class BridgeNameDoesNotExistException(BaseCustomException):
    """Exception raised when a bridge name does not exist."""

    def __init__(self, *args):
        """Initialize BridgeNameDoesNotExistException with optional arguments"""
        super().__init__(*args)


class UnexpectedDataArguments(BaseCustomException):
    """Exception raised when unexpected data arguments are provided."""

    def __init__(self, *args):
        """Initialize UnexpectedDataArguments with optional arguments."""
        super().__init__(*args)


class InterfaceInsertionError(BaseCustomException):
    """Exception raised when an error occurs during interface insertion."""

    def __init__(self, *args):
        """Initialize InterfaceInsertionError with optional arguments."""
        super().__init__(*args)


class CreateInterfaceDataException(BaseCustomException):
    """Exception raised when there is an error creating interface data."""

    def __init__(self, *args):
        """Initialize CreateInterfaceDataException with optional arguments."""
        super().__init__(*args)


class InterfaceDeletingError(BaseCustomException):
    """Exception raised when an error occurs during interface deletion."""

    def __init__(self, *args):
        """Initialize InterfaceDeletingError with optional arguments."""
        super().__init__(*args)


class NetplanApplyException(BaseCustomException):
    """Exception raised when an error occurs applying a Netplan configuration"""

    def __init__(self, *args):
        """Initialize NetplanApplyException with optional arguments."""
        super().__init__(*args)
