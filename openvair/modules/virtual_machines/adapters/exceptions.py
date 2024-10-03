"""Module for custom exceptions related to virtual machine.

Classes:
    DBCannotBeConnectedError: Exception raised when a database connection cannot
        be established.
"""


class DBCannotBeConnectedError(Exception):
    """Exception raised when a database connection cannot be established.

    This exception is used to signal that the application was unable to
    connect to the database required for virtual machine operations.

    Attributes:
        message (str): The error message describing the connection issue.
    """

    def __init__(self, message: str):
        """Initialize the DBCannotBeConnectedError.

        Args:
            message (str): The error message describing the connection issue.
        """
        self.message = message
        super(DBCannotBeConnectedError, self).__init__(message)

    def __str__(self) -> str:
        """Return the error message.

        Returns:
            str: The error message.
        """
        return self.message
