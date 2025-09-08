"""Module for defining custom exceptions in the volume service layer.

This module contains custom exception classes that are used to handle
various error conditions specific to the volume service layer. These
exceptions help in managing errors related to volume operations, such as
unexpected data arguments, validation errors, and issues with storage
availability.

Classes:
    UnexpectedDataArguments: Raised when unexpected data arguments are
        encountered.
    CreateVolumeDataException: Raised when there is an error with the data
        required to create a volume.
    VolumeStatusException: Raised when there is an issue with the status of a
        volume.
    VolumeHasAttachmentError: Raised when a volume is found to have
        attachments, preventing certain operations.
    ValidateArgumentsError: Raised when there is an error in validating
        arguments.
    VolumeExistsOnStorageException: Raised when a volume already exists on
        the specified storage.
    StorageUnavailableException: Raised when the storage is unavailable.
    VolumeHasNotStorage: Raised when a volume does not have an associated
        storage.
    VmPowerStateIsNotShutOffException: Raised when the VM power state is not
        shut off.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class UnexpectedDataArguments(BaseCustomException):
    """Raised when unexpected data arguments are encountered."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize UnexpectedDataArguments"""
        super().__init__(message, *args)


class CreateVolumeDataException(BaseCustomException):
    """Raised when error with the data required to create a volume."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CreateVolumeDataException"""
        super().__init__(message, *args)


class VolumeStatusException(BaseCustomException):
    """Raised when there is an issue with the status of a volume."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VolumeStatusException"""
        super().__init__(message, *args)


class VolumeHasAttachmentError(BaseCustomException):
    """Raised when a volume is found to have attachments"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VolumeHasAttachmentError"""
        super().__init__(message, *args)


class ValidateArgumentsError(BaseCustomException):
    """Raised when there is an error in validating arguments."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ValidateArgumentsError"""
        super().__init__(message, *args)


class VolumeExistsOnStorageException(BaseCustomException):
    """Raised when a volume already exists on the specified storage."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VolumeExistsOnStorageException"""
        super().__init__(message, *args)


class StorageUnavailableException(BaseCustomException):
    """Raised when the storage is unavailable."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageUnavailableException"""
        super().__init__(message, *args)


class VolumeHasNotStorage(BaseCustomException):
    """Raised when a volume does not have an associated storage."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VolumeHasNotStorage"""
        super().__init__(message, *args)


class VmPowerStateIsNotShutOffException(BaseCustomException):
    """Raised when the VM power state is not shut off."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VmPowerStateIsNotShutOffException"""
        super().__init__(message, *args)


class VolumeNotFoundException(BaseCustomException):
    """Raised when a volume is not found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize VolumeNotFoundException"""
        super().__init__(message, *args)


class StorageNotFoundException(BaseCustomException):
    """Raised when can't get info about the storage."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageNotFoundException"""
        super().__init__(message, *args)
