"""Custom exceptions for RemoteFS volume operations.

This module defines custom exceptions that are specific to operations related
to RemoteFS volumes. These exceptions handle errors that may occur during
volume creation, deletion, and extension.

Classes:
    QemuImgCreateException: Raised when there is an error creating a volume
        with `qemu-img`.
    QemuImgExtendException: Raised when there is an error extending a volume
        with `qemu-img`.
    DeleteVolumeException: Raised when there is an error deleting a volume.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class QemuImgCreateException(BaseCustomException):
    """Exception raised when error creating a volume with `qemu-img`."""

    def __init__(self, *args):
        """Initialize the QemuImgCreateException"""
        super().__init__(*args)


class QemuImgExtendException(BaseCustomException):
    """Exception raised an error extending a volume with `qemu-img`."""

    def __init__(self, *args):
        """Initialize the QemuImgExtendException"""
        super().__init__(*args)


class DeleteVolumeException(BaseCustomException):
    """Exception raised an error deleting a volume."""

    def __init__(self, *args):
        """Initialize the DeleteVolumeException"""
        super().__init__(*args)
