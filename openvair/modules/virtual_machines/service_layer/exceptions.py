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

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class UnexpectedDataArguments(BaseCustomException):
    """Raised when unexpected arguments are passed to a function."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize UnexpectedDataArguments with optional arguments."""
        super().__init__(message, *args)


class CreateVMDataException(BaseCustomException):
    """Raised when error with the data for creating a virtual machine."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CreateVMDataException with optional arguments."""
        super().__init__(message, *args)


class VMStatusException(BaseCustomException):
    """Raised when there is an error with the status of a virtual machine."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VMStatusException with optional arguments."""
        super().__init__(message, *args)


class VMPowerStateException(BaseCustomException):
    """Raised when error with the power state of a virtual machine."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VMPowerStateException with optional arguments."""
        super().__init__(message, *args)


class ValidateArgumentsError(BaseCustomException):
    """Raised when argument validation fails."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ValidateArgumentsError with optional arguments."""
        super().__init__(message, *args)


class VolumeStatusIsError(BaseCustomException):
    """Raised when there is an issue with the status of a volume."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VolumeStatusIsError with optional arguments."""
        super().__init__(message, *args)


class ComesEmptyVolumeInfo(BaseCustomException):
    """Raised when the volume information is empty or invalid."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ComesEmptyVolumeInfo with optional arguments."""
        super().__init__(message, *args)


class MaxTriesError(BaseCustomException):
    """Raised when the maximum number of tries for an operation is exceeded."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize MaxTriesError with optional arguments."""
        super().__init__(message, *args)
