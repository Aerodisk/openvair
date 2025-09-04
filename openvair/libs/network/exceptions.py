"""Network exceptions for Open vAIR.

This module provides exceptions for network-related operations in the
Open vAIR system.

Classes:
    NetworkException: Base exception for network operations.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NetworkException(BaseCustomException):
    """Base exception for network operations."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401
        """Initialize the NetworkException with a message."""
        super().__init__(message, *args)


class WebsockifyStartupError(NetworkException):
    """Raised when websockify fails to start."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401
        """Initialize the WebsockifyStartupError with a message."""
        super().__init__(message, *args)
