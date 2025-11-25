"""Custom exceptions for the notification service layer.

This module defines custom exceptions that are used within the notification
service layer.

Classes:
    - NotificationNotFoundError: Raised when a notification is not found.
    - NotificationServiceNotKnown: Raised when the notification service is
        not recognized.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NotificationNotFoundError(BaseCustomException):
    """Exception raised when a notification is not found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the NotificationNotFoundError."""
        super().__init__(message, *args)


class NotificationServiceNotKnown(BaseCustomException):
    """Exception raised when the notification service is not recognized."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the NotificationServiceNotKnown."""
        super().__init__(message, *args)
