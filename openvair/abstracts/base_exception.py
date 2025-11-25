"""Custom base exception class.

This module defines a base class for custom exceptions, providing a framework
for creating exceptions with detailed error messages.

Classes:
    BaseCustomException: A base class for custom exceptions that includes
        message handling and string representation.
"""

from typing import Any


class BaseCustomException(Exception):  # noqa: N818 need complex rename if change this class
    """A base class for custom exceptions.

    This class extends the standard Python Exception class and adds support
    for detailed error messages, which can be either a string or a tuple.

    Attributes:
        message (str): The error message associated with the exception.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the BaseCustomException.

        Args:
            message (str): The error message to associate with this exception.
            *args: Additional arguments to pass to the base Exception class.
        """
        self.message = message
        super().__init__(message, *args)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        If the message is a tuple, only the first element is returned in the
        string representation. Otherwise, the full message is returned.

        Returns:
            str: The string representation of the exception, including its
            class name and message.
        """
        if self.message:
            if isinstance(self.message, tuple):
                return f'{self.__class__.__name__}: {self.message[0]}'
            return f'{self.__class__.__name__}: {self.message}'
        return f'{self.__class__.__name__}: raised.'
