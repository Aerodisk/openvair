"""Custom exceptions for the notification adapters.

This module defines custom exceptions that are used within the notification
adapters.
"""


class DBCannotBeConnectedError(Exception):
    """Exception raised when the database cannot be connected."""

    def __init__(self, message: str):
        """Initialize the DBCannotBeConnectedError.

        Args:
            message (str): The error message to associate with this exception.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        Returns:
            str: The error message.
        """
        return self.message
