"""This module defines exceptions for the block device module.

Classes:
    DBCannotBeConnectedError: Exception raised when the database cannot
        be connected.
"""


class DBCannotBeConnectedError(Exception):
    """Exception raised when database cannot be connected"""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message

        Args:
            message (str): Message with additional information about
                the exception.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self) -> str:
        """Return the exception message.

        Returns:
            str: The exception message.
        """
        return self.message
