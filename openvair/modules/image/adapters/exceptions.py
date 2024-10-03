"""Module containing custom exceptions for the image adapter.

This module defines exceptions that are raised in specific error conditions
related to the image adapter, particularly in scenarios involving database
connection issues.

Classes:
    DBCannotBeConnectedError: Exception raised when the database connection
        cannot be established.
"""


class DBCannotBeConnectedError(Exception):
    """Exception raised when the database connection cannot be established.

    This exception is used to signal that a connection to the database could
    not be made, often due to issues such as incorrect configuration, network
    problems, or the database service being unavailable.
    """

    def __init__(self, message: str):
        """Initialize DBCannotBeConnectedError with a message.

        Args:
            message (str): A description of the error that occurred.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return the error message as a string.

        Returns:
            str: The error message provided during initialization.
        """
        return self.message
