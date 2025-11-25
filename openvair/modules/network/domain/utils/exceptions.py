"""Custom exceptions for OVS management and network interface errors.

This module defines custom exceptions used for handling errors related to
Open vSwitch (OVS) management and network interface operations.

Classes:
    OVSManagerException: Exception raised for errors in OVS management.
    BridgeNotFoundException: Exception raised when a bridge is not found.
    InterfaceNotFoundException: Exception raised when an interface is not found.
    InvalidAddressException: Exception raised for invalid IP addresses.
    NetworkInterfaceException: Exception raised for network interface errors.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class OVSManagerException(BaseCustomException):
    """Exception raised for errors in OVS management."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize OVSManagerException with optional arguments."""
        super().__init__(message, *args)


class BridgeNotFoundException(OVSManagerException):
    """Exception raised when a bridge is not found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize BridgeNotFoundException with optional arguments."""
        super().__init__(message, *args)


class InterfaceNotFoundException(OVSManagerException):
    """Exception raised when an interface is not found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize InterfaceNotFoundException with optional arguments."""
        super().__init__(message, *args)


class InvalidAddressException(OVSManagerException):
    """Exception raised for invalid IP addresses."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize InvalidAddressException with optional arguments."""
        super().__init__(message, *args)


class IPManagerException(BaseCustomException):
    """Exception raised for network interface errors."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NetworkInterfaceException with optional arguments."""
        super().__init__(message, *args)
