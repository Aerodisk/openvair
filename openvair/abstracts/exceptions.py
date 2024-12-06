"""Module contains exceptions for the abstract classes of the entire project.

Classes:
    DBCannotBeConnectedError: Exception raised when the database cannot
        be connected.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class DBCannotBeConnectedError(Exception):
    """Exception raised when database cannot be connected"""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message

        Args:
            message (str): Message with additional information about
                the exception.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return the exception message.

        Returns:
            str: The exception message.
        """
        return self.message


class ConfigParameterNotSpecifiedError(BaseCustomException):
    """Raised when exception KeyError while getting from project config"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ConfigParameterNotSpecifiedError exception."""
        super().__init__(message, *args)
