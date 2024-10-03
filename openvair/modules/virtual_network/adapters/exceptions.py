"""Custom exceptions for the virtual network adapter.

This module defines custom exceptions that are used within the virtual network
adapter layer.

Classes:
    - DBCannotBeConnectedError: Raised when unable to connect to the database.
"""


class DBCannotBeConnectedError(Exception):
    """Exception raised when unable to connect to the database.

    Attributes:
        message (str): The error message.
    """

    def __init__(self, message: str):
        """Initialize the DBCannotBeConnectedError.

        Args:
            message (str): The error message.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self):
        """Return the error message."""
        return self.message
