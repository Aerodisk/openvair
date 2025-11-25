"""Custom exceptions for the storage service layer.

This module defines custom exceptions that are specific to the storage service
layer. These exceptions are used to handle various error conditions that can
occur during storage operations, such as creating, deleting, or managing
storage entities.

Classes:
    StorageExistsError: Raised when attempting to create a storage that already
        exists.
    StorageStatusError: Raised when an invalid storage status is encountered.
    StorageAttributeError: Raised when required storage attributes are missing
        or incorrect.
    StorageNotFoundError: Raised when the requested storage is not found.
    StorageHasVolumesOrImages: Raised when a storage cannot be deleted because
        it has associated volumes or images.
    DeviceDoesNotExist: Raised when a specified device does not exist.
    GetEmptyDomainStorageInfo: Raised when storage information is unexpectedly
        empty.
    CannotDeleteSystemPartition: Raised when attempting to delete a system
        partition.
    CannotCreateStorageOnRootOfSystemDisk: Raised when trying to create storage
        on the root of a system disk.
    CannotCreateStorageOnSystemPartition: Raised when trying to create storage
        on a system partition.
    PartitionHasStorage: Raised when trying to delete a partition that still
        has associated storage.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class StorageExistsError(BaseCustomException):
    """Exception raised when storage with the name or specifications exists."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageExistsError"""
        super().__init__(message, *args)


class StorageStatusError(BaseCustomException):
    """Exception raised when an invalid storage status is encountered."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageStatusError"""
        super().__init__(message, *args)


class StorageAttributeError(BaseCustomException):
    """Exception raised when storage attributes are missing or incorrect."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageAttributeError"""
        super().__init__(message, *args)


class StorageNotFoundError(BaseCustomException):
    """Exception raised when the requested storage is not found."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageNotFoundError"""
        super().__init__(message, *args)


class StorageHasObjects(BaseCustomException):
    """Exception raised when a storage cannot be deleted

    Because it has associated volumes, images, template or another object on the
    storage.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize StorageHasVolumesOrImages"""
        super().__init__(message, *args)


class DeviceDoesNotExist(BaseCustomException):
    """Exception raised when a specified device does not exist."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize DeviceDoesNotExist"""
        super().__init__(message, *args)


class GetEmptyDomainStorageInfo(BaseCustomException):
    """Exception raised when storage information is unexpectedly empty."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize GetEmptyDomainStorageInfo"""
        super().__init__(message, *args)


class CannotDeleteSystemPartition(BaseCustomException):
    """Exception raised when attempting to delete a system partition."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CannotDeleteSystemPartition"""
        super().__init__(message, *args)


class CannotCreateStorageOnRootOfSystemDisk(BaseCustomException):
    """Exception raised when cannot create storage on root of a system disk."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CannotCreateStorageOnRootOfSystemDisk"""
        super().__init__(message, *args)


class CannotCreateStorageOnSystemPartition(BaseCustomException):
    """Exception raised when trying to create storage on a system partition."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CannotCreateStorageOnSystemPartition"""
        super().__init__(message, *args)


class PartitionHasStorage(BaseCustomException):
    """Exception raised when trying to delete a partition that has storage."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize PartitionHasStorage"""
        super().__init__(message, *args)
