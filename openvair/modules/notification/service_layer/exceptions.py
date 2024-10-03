"""Custom exceptions for the notification service layer.

This module defines custom exceptions that are used within the notification
service layer.

Classes:
    - NotificationNotFoundError: Raised when a notification is not found.
    - NotificationServiceNotKnown: Raised when the notification service is
        not recognized.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class NotificationNotFoundError(BaseCustomException):
    """Exception raised when a notification is not found."""

    def __init__(self, *args):
        """Initialize the NotificationNotFoundError.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class NotificationServiceNotKnown(BaseCustomException):
    """Exception raised when the notification service is not recognized."""

    def __init__(self, *args):
        """Initialize the NotificationServiceNotKnown.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)
