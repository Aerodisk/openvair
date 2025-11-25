"""Custom exceptions for SNMP operations.

This module defines custom exceptions used in the SNMP domain for handling
errors related to SNMP agent operations.

Classes:
    SNMPAgentTypeError: Exception raised for errors in SNMP agent type.
    SNMPModuleRegistrationError: Exception raised when module registration
        fails.
    SNMPConnectionError: Exception raised for connection-related errors.
    SNMPStartupError: Exception raised when agent fails to start.
    SNMPShutdownError: Exception raised when agent fails to stop.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class SNMPAgentTypeError(BaseCustomException):
    """Exception raised for errors in SNMP agent type."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize SNMPAgentTypeError with optional arguments."""
        super().__init__(message, *args)


class SNMPModuleRegistrationError(BaseCustomException):
    """Exception raised when SNMP module registration fails."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize SNMPModuleRegistrationError."""
        super().__init__(message, *args)


class SNMPConnectionError(BaseCustomException):
    """Exception raised for SNMP connection-related errors."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize SNMPConnectionError."""
        super().__init__(message, *args)


class SNMPAgentStartError(BaseCustomException):
    """Exception raised when SNMP agent fails to start."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize SNMPStartupError."""
        super().__init__(message, *args)


class SNMPAgentStopError(BaseCustomException):
    """Exception raised when SNMP agent fails to stop."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize SNMPShutdownError."""
        super().__init__(message, *args)
