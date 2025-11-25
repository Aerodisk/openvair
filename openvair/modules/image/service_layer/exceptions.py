"""Exception classes for the image service layer.

This module defines custom exceptions used in the image service layer. These
exceptions handle specific error conditions that may arise during image
operations, such as unexpected data, upload errors, or issues related to
image status or storage.

Classes:
    UnexpectedDataArguments: Raised when unexpected data arguments are provided.
    UploadImageDataError: Raised when there is an error during image data
        upload.
    ImageHasAttachmentError: Raised when an operation is attempted on an image
        that has existing attachments.
    ImageStatusError: Raised when there is an error related to the image status.
    ValidateArgumentsError: Raised when there is an error in validating
        arguments.
    StorageUnavailableException: Raised when the storage is unavailable.
    ImageHasNotStorage: Raised when an image does not have a corresponding
        storage.
    ImageHasSameAttachment: Raised when an image has the same attachment
        already.
    ImageNameExistsException: Raised when an image with the same name already
        exists.
    ImageDeletingError: Raised when an error occurs during image deletion.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class UnexpectedDataArguments(BaseCustomException):
    """Raised when unexpected data arguments are provided."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UnexpectedDataArguments exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class UploadImageDataError(BaseCustomException):
    """Raised when there is an error during image data upload."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UploadImageDataError exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageHasAttachmentError(BaseCustomException):
    """Raised when an operation is attempted on an image with attachments."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageHasAttachmentError exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageStatusError(BaseCustomException):
    """Raised when there is an error related to the image status."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageStatusError exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ValidateArgumentsError(BaseCustomException):
    """Raised when there is an error in validating arguments."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ValidateArgumentsError exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class StorageUnavailableException(BaseCustomException):
    """Raised when the storage is unavailable."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the StorageUnavailableException exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageHasNotStorage(BaseCustomException):
    """Raised when an image does not have a corresponding storage."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageHasNotStorage exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageHasSameAttachment(BaseCustomException):
    """Raised when an image has the same attachment already."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageHasSameAttachment exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageNameExistsException(BaseCustomException):
    """Raised when an image with the same name already exists."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageNameExistsException exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageDeletingError(BaseCustomException):
    """Raised when an error occurs during image deletion."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageDeletingError exception.

        Args:
            message (str): Message with info about exception.
            *args: Variable length argument list.
        """
        super().__init__(message, *args)


class ImageUnvailableError(BaseCustomException):
    """Raised when checking existance image by ist path"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the ImageUnvailableError exception."""
        super().__init__(message, *args)
