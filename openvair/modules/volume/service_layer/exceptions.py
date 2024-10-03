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

from openvair.modules.tools.base_exception import BaseCustomException


class UnexpectedDataArguments(BaseCustomException):
    """Raised when unexpected data arguments are encountered."""

    def __init__(self, *args):
        """Initialize UnexpectedDataArguments"""
        super().__init__(*args)


class CreateVolumeDataException(BaseCustomException):
    """Raised when error with the data required to create a volume."""

    def __init__(self, *args):
        """Initialize CreateVolumeDataException"""
        super().__init__(*args)


class VolumeStatusException(BaseCustomException):
    """Raised when there is an issue with the status of a volume."""

    def __init__(self, *args):
        """Initialize VolumeStatusException"""
        super().__init__(*args)


class VolumeHasAttachmentError(BaseCustomException):
    """Raised when a volume is found to have attachments"""

    def __init__(self, *args):
        """Initialize VolumeHasAttachmentError"""
        super().__init__(*args)


class ValidateArgumentsError(BaseCustomException):
    """Raised when there is an error in validating arguments."""

    def __init__(self, *args):
        """Initialize ValidateArgumentsError"""
        super().__init__(*args)


class VolumeExistsOnStorageException(BaseCustomException):
    """Raised when a volume already exists on the specified storage."""

    def __init__(self, *args):
        """Initialize VolumeExistsOnStorageException"""
        super().__init__(*args)


class StorageUnavailableException(BaseCustomException):
    """Raised when the storage is unavailable."""

    def __init__(self, *args):
        """Initialize StorageUnavailableException"""
        super().__init__(*args)


class VolumeHasNotStorage(BaseCustomException):
    """Raised when a volume does not have an associated storage."""

    def __init__(self, *args):
        """Initialize VolumeHasNotStorage"""
        super().__init__(*args)


class VmPowerStateIsNotShutOffException(BaseCustomException):
    """Raised when the VM power state is not shut off."""

    def __init__(self, *args):
        """Initialize VmPowerStateIsNotShutOffException"""
        super().__init__(*args)
