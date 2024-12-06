"""Exception classes for the image domain layer.

This module defines custom exceptions used in the image domain layer,
particularly for handling errors related to image storage operations.

Classes:
    ImageDoesNotExistOnStorage: Exception raised when an image does not
        exist on the storage.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class ImageDoesNotExistOnStorage(BaseCustomException):
    """Exception raised when an image does not exist on the storage.

    This exception is used to signal that an operation was attempted on an
    image that is expected to be present on the storage but could not be
    found.

    Args:
        BaseCustomException (type): Parent exception class.
    """

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageDoesNotExistOnStorage exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)
