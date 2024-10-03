"""Custom exceptions for the volume domain module.

This module defines custom exceptions that are specific to operations within
the volume domain. These exceptions handle error conditions related to volume
management, particularly when interacting with storage systems.

Classes:
    VolumeDoesNotExistOnStorage: Raised when a specified volume does not exist
        on the storage.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class VolumeDoesNotExistOnStorage(BaseCustomException):
    """Exception raised when a specified volume does not exist on the storage.

    This exception is used to indicate that the system could not find a volume
    on the storage system, which may be due to incorrect volume ID or path,
    or the volume might have been deleted or never created.

    Attributes:
        message (str): A message describing the error.
    """

    def __init__(self, *args):
        """Initialize the VolumeDoesNotExistOnStorage.

        Args:
            *args: Variable length argument list containing the error message.
        """
        super().__init__(*args)
