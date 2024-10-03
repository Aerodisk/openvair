"""Custom exceptions for the volume adapters module.

This module defines custom exceptions that are specific to the volume adapters.
These exceptions handle error conditions related to database connections and
other adapter-related issues.

Classes:
    DBCannotBeConnectedError: Raised when a database connection cannot be
        established.
"""


class DBCannotBeConnectedError(Exception):
    """Exception raised when the database cannot be connected.

    This exception is used to indicate that the system is unable to establish
    a connection with the database, which may be due to configuration issues,
    network problems, or other related errors.

    Attributes:
        message (str): A message describing the connection error.
    """

    def __init__(self, message: str):
        """Initialize the DBCannotBeConnectedError with a specific message.

        Args:
            message (str): A descriptive error message.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self):
        """Return the error message as the string representation of exception.

        Returns:
            str: The error message.
        """
        return self.message
