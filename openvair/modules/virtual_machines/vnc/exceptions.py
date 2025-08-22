"""Exception classes for the VNC management subsystem.

This module defines custom exceptions used in the VNC management system,
particularly for handling errors related to VNC session operations.

Classes:
    VncManagerError: Base exception for VNC manager operations.
    VncPortAllocationError: Raised when VNC port allocation fails.
    VncProcessNotFoundError: Raised when websockify process cannot be found.
    VncSessionStartupError: Raised when VNC session startup fails.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class VncManagerError(BaseCustomException):
    """Base exception for VNC manager operations."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401
        """Initialize the VncManagerError with a message."""
        super().__init__(message, *args)


class VncPortAllocationError(VncManagerError):
    """Raised when VNC port allocation fails."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401
        """Initialize the VncPortAllocationError with a message."""
        super().__init__(message, *args)


class VncProcessNotFoundError(VncManagerError):
    """Raised when websockify process cannot be found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401
        """Initialize the VncProcessNotFoundError with a message."""
        super().__init__(message, *args)


class VncSessionStartupError(VncManagerError):
    """Raised when VNC session startup fails."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401
        """Initialize the VncSessionStartupError with a message."""
        super().__init__(message, *args)
