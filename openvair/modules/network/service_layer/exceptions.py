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

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class InterfaceNotFoundError(BaseCustomException):
    """Exception raised when a network interface is not found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize InterfaceNotFoundError with optional arguments."""
        super().__init__(message, *args)


class BridgeNameExistException(BaseCustomException):
    """Exception raised when a bridge name already exists."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize BridgeNameExistException with optional arguments."""
        super().__init__(message, *args)


class BridgeNameDoesNotExistException(BaseCustomException):
    """Exception raised when a bridge name does not exist."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize BridgeNameDoesNotExistException with optional arguments"""
        super().__init__(message, *args)


class UnexpectedDataArguments(BaseCustomException):
    """Exception raised when unexpected data arguments are provided."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize UnexpectedDataArguments with optional arguments."""
        super().__init__(message, *args)


class InterfaceInsertionError(BaseCustomException):
    """Exception raised when an error occurs during interface insertion."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize InterfaceInsertionError with optional arguments."""
        super().__init__(message, *args)


class CreateInterfaceDataException(BaseCustomException):
    """Exception raised when there is an error creating interface data."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CreateInterfaceDataException with optional arguments."""
        super().__init__(message, *args)


class InterfaceDeletingError(BaseCustomException):
    """Exception raised when an error occurs during interface deletion."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize InterfaceDeletingError with optional arguments."""
        super().__init__(message, *args)


class NetplanApplyException(BaseCustomException):
    """Exception raised when an error occurs applying a Netplan configuration"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NetplanApplyException with optional arguments."""
        super().__init__(message, *args)


class NestedOVSBridgeNotAllowedError(BaseCustomException):
    """Raised when try add ovs brindge into ovs bridge like a port"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NestedOVSBridgeNotAllowedError"""
        super().__init__(message, *args)


class InerfaceAllreadyExistException(BaseCustomException):
    """Raised when try create inetrface with existing name"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize InerfaceAllreadyExistException"""
        super().__init__(message, *args)
