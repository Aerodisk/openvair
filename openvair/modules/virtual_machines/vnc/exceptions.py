"""Exceptions for VNC port management system.

This module defines custom exceptions used throughout the VNC port management
system to provide precise error handling for different failure scenarios.
"""

from openvair.abstracts.base_exception import BaseCustomException


class VncPortPoolExhaustedException(BaseCustomException):
    """Raised when no free ports are available in the VNC port pool.

    This exception is raised when all ports in the configured range are
    either allocated or in use, preventing new VNC sessions from starting.
    """

    def __init__(self, message: str, *args: object) -> None:
        """Initialize VncPortPoolExhaustedException.

        Args:
            message: Exception message
            *args: Additional arguments
        """
        super().__init__(message, *args)


class VncPortAllocationError(BaseCustomException):
    """Raised when port allocation fails due to system errors.

    This exception indicates system-level failures during port allocation,
    such as file I/O errors, permission issues, or lock acquisition failures.
    """

    def __init__(self, message: str, *args: object) -> None:
        """Initialize VncPortAllocationError.

        Args:
            message: Exception message
            *args: Additional arguments
        """
        super().__init__(message, *args)


class WebsockifyProcessError(BaseCustomException):
    """Raised when websockify process management fails.

    This exception covers failures in starting, stopping, or managing
    websockify processes, including process startup failures and PID
    detection issues.
    """

    def __init__(self, message: str, *args: object) -> None:
        """Initialize WebsockifyProcessError.

        Args:
            message: Exception message
            *args: Additional arguments
        """
        super().__init__(message, *args)


class VncSessionCoordinationError(BaseCustomException):
    """Raised when VNC session coordination fails.

    This exception is raised when the coordination between port allocation
    and process management fails, indicating a problem with the overall
    session management workflow.
    """

    def __init__(self, message: str, *args: object) -> None:
        """Initialize VncSessionCoordinationError.

        Args:
            message: Exception message
            *args: Additional arguments
        """
        super().__init__(message, *args)
