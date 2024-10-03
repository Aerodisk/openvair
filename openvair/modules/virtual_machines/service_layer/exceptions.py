"""Module for custom exceptions in the virtual machines service layer.

This module defines custom exceptions that are used throughout the virtual
machines service layer. These exceptions extend the `BaseCustomException`
class from the `tools` module and are used to handle specific error cases
involving virtual machine operations.

Classes:
    UnexpectedDataArguments: Raised when unexpected arguments are passed
        to a function.
    CreateVMDataException: Raised when there is an error with the data
        provided for creating a virtual machine.
    VMStatusException: Raised when there is an error with the status of
        a virtual machine.
    VMPowerStateException: Raised when there is an error with the power
        state of a virtual machine.
    ValidateArgumentsError: Raised when argument validation fails.
    VolumeStatusIsError: Raised when there is an issue with the status
        of a volume.
    ComesEmptyVolumeInfo: Raised when the volume information is empty
        or invalid.
    MaxTriesError: Raised when the maximum number of tries for an operation
        is exceeded.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class UnexpectedDataArguments(BaseCustomException):
    """Raised when unexpected arguments are passed to a function."""

    def __init__(self, *args):
        """Initialize UnexpectedDataArguments with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class CreateVMDataException(BaseCustomException):
    """Raised when error with the data for creating a virtual machine."""

    def __init__(self, *args):
        """Initialize CreateVMDataException with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class VMStatusException(BaseCustomException):
    """Raised when there is an error with the status of a virtual machine."""

    def __init__(self, *args):
        """Initialize VMStatusException with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class VMPowerStateException(BaseCustomException):
    """Raised when error with the power state of a virtual machine."""

    def __init__(self, *args):
        """Initialize VMPowerStateException with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class ValidateArgumentsError(BaseCustomException):
    """Raised when argument validation fails."""

    def __init__(self, *args):
        """Initialize ValidateArgumentsError with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class VolumeStatusIsError(BaseCustomException):
    """Raised when there is an issue with the status of a volume."""

    def __init__(self, *args):
        """Initialize VolumeStatusIsError with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class ComesEmptyVolumeInfo(BaseCustomException):
    """Raised when the volume information is empty or invalid."""

    def __init__(self, *args):
        """Initialize ComesEmptyVolumeInfo with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class MaxTriesError(BaseCustomException):
    """Raised when the maximum number of tries for an operation is exceeded."""

    def __init__(self, *args):
        """Initialize MaxTriesError with optional arguments.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)
