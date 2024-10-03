"""Exception classes for network module adapters.

This module defines custom exceptions used in the network module adapters,
particularly for handling database connection errors.

Classes:
    DBCannotBeConnectedError: Raised when a database connection cannot be
        established.
"""


class DBCannotBeConnectedError(Exception):
    """Raised when a database connection cannot be established."""

    def __init__(self, message: str):
        """Initialize the DBCannotBeConnectedError exception.

        Args:
            message (str): The error message describing the connection issue.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self):
        """Return the error message as a string."""
        return self.message
