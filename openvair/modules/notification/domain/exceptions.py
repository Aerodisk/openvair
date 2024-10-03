"""Custom exceptions for notification domain.

This module defines custom exceptions that are used within the notification
domain, particularly for email notifications.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class NoRecipientsSpecifiedForEmailNotification(BaseCustomException):
    """Raised when recipients are not specified for email notification."""

    def __init__(self, *args):
        """Initialize the `NoRecipientsSpecifiedForEmailNotification`.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)
