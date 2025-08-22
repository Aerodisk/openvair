"""Exceptions for VNC port management system."""

from typing import Any
from openvair.abstracts.base_exception import BaseCustomException


class VncPortPoolExhaustedException(BaseCustomException):
    """Raised when no free ports are available in the VNC port pool."""
    
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class VncPortAllocationError(BaseCustomException):
    """Raised when port allocation fails due to system errors."""
    
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class WebsockifyProcessError(BaseCustomException):
    """Raised when websockify process management fails."""
    
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class VncSessionCoordinationError(BaseCustomException):
    """Raised when VNC session coordination fails."""
    
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)
