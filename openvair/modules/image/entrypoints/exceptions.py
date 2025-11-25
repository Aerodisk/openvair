"""Custom exceptions for the Image entrypoints.

This module defines custom exceptions used in the Image entrypoints module
to handle specific error cases, such as unsupported file extensions or
validation issues.

Classes:
    NotSupportedExtensionError: Raised when an unsupported file extension
        is encountered during image upload.
    FilenameLengthError: Raised when a file name exceeds the allowed length.
    CreateImagePageException: Raised when invalid arguments are provided
        for creating an image page.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NotSupportedExtensionError(BaseCustomException):
    """Exception raised for unsupported file extensions.

    This exception is triggered when an image file with an unsupported
    extension is uploaded.

    Args:
        message (str): The error message describing the issue.
        *args (Any): Additional arguments for exception initialization.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with the given arguments.

        Args:
            message (str): The error message describing the issue.
            *args (Any): Additional arguments for exception initialization.
        """
        super().__init__(message, *args)


class FilenameLengthError(BaseCustomException):
    """Exception raised when a file name exceeds the allowed length.

    This exception is triggered when the length of an image file name
    exceeds the maximum limit.

    Args:
        message (str): The error message describing the issue.
        *args (Any): Additional arguments for exception initialization.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with the given arguments.

        Args:
            message (str): The error message describing the issue.
            *args (Any): Additional arguments for exception initialization.
        """
        super().__init__(message, *args)


class CreateImagePageException(BaseCustomException):
    """Exception raised when invalid arguments are provided for image pages.

    This exception is triggered when the `ImagesPage` class or related
    functionality receives incorrect arguments.

    Args:
        message (str): The error message describing the issue.
        *args (Any): Additional arguments for exception initialization.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with the given arguments.

        Args:
            message (str): The error message describing the issue.
            *args (Any): Additional arguments for exception initialization.
        """
        super().__init__(message, *args)
