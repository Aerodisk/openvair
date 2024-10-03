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

from openvair.modules.tools.base_exception import BaseCustomException


class OVSManagerException(BaseCustomException):
    """Exception raised for errors in OVS management."""

    def __init__(self, *args):
        """Initialize OVSManagerException with optional arguments."""
        super(OVSManagerException, self).__init__(args)


class BridgeNotFoundException(OVSManagerException):
    """Exception raised when a bridge is not found."""

    def __init__(self, *args):
        """Initialize BridgeNotFoundException with optional arguments."""
        super(BridgeNotFoundException, self).__init__(args)


class InterfaceNotFoundException(OVSManagerException):
    """Exception raised when an interface is not found."""

    def __init__(self, *args):
        """Initialize InterfaceNotFoundException with optional arguments."""
        super(InterfaceNotFoundException, self).__init__(args)


class InvalidAddressException(OVSManagerException):
    """Exception raised for invalid IP addresses."""

    def __init__(self, *args):
        """Initialize InvalidAddressException with optional arguments."""
        super(InvalidAddressException, self).__init__(args)


class NetworkInterfaceException(BaseCustomException):
    """Exception raised for network interface errors."""

    def __init__(self, *args):
        """Initialize NetworkInterfaceException with optional arguments."""
        super().__init__(args)

class NetworkIPManagerException(BaseCustomException):
    """Exception raised for IPManager working exception."""

    def __init__(self, *args):
        """Initialize NetworkIPManagerException with optional arguments."""
        super().__init__(args)
