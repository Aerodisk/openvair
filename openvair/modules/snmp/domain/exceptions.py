"""Custom exceptions for SNMP operations.

This module defines custom exceptions used in the SNMP domain for handling
errors related to SNMP agent operations.

Classes:
    SNMPAgenTypeError: Exception raised for errors in SNMP agent type.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class SNMPAgenTypeError(BaseCustomException):
    """Exception raised for errors in SNMP agent type."""

    def __init__(self, *args):
        """Initialize SNMPAgenTypeError with optional arguments."""
        super().__init__(args)
