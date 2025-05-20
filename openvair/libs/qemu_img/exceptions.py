"""Exception definitions for the qemu-img adapter.

This module defines custom exception classes used in the qemu-img adapter
for handling command execution failures and providing meaningful error
messages.

Classes:
    QemuImgError: Base exception for all qemu-img-related failures.
"""

from openvair.abstracts.base_exception import BaseCustomException


class QemuImgError(BaseCustomException):
    """Base exception class for qemu-img operations.

    This exception is raised when a qemu-img command fails during execution.
    It encapsulates error information from the command output and provides
    a unified interface for handling qemu-img related failures.

    Inherits from:
        BaseCustomException

    Typical usage:
        raise QemuImgError("Failed to create qcow2 image")
    """

    ...
