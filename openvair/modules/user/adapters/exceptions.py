"""Custom exceptions for the user module.

This module defines custom exceptions used within the user management
module. Custom exceptions allow for more specific error handling and
improved readability of error messages.

Exceptions:
    - DBCannotBeConnectedError: Raised when a database connection cannot
        be established.
"""

class DBCannotBeConnectedError(Exception):
    """Exception raised when a database connection cannot be established.

    Attributes:
        message (str): A description of the error.
    """

    def __init__(self, message: str):
        """Initialize the exception with an error message.

        Args:
            message (str): A description of the error.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return a string representation of the exception.

        Returns:
            str: The error message.
        """
        return self.message
