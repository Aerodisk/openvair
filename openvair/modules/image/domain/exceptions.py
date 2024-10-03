"""Exception classes for the image domain layer.

This module defines custom exceptions used in the image domain layer,
particularly for handling errors related to image storage operations.

Classes:
    ImageDoesNotExistOnStorage: Exception raised when an image does not
        exist on the storage.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class ImageDoesNotExistOnStorage(BaseCustomException):
    """Exception raised when an image does not exist on the storage.

    This exception is used to signal that an operation was attempted on an
    image that is expected to be present on the storage but could not be
    found.

    Args:
        BaseCustomException (type): Parent exception class.
    """

    def __init__(self, *args):
        """Initialize the ImageDoesNotExistOnStorage exception.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(args)
