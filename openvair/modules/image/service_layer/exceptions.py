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

from openvair.modules.tools.base_exception import BaseCustomException


class UnexpectedDataArguments(BaseCustomException):
    """Raised when unexpected data arguments are provided."""

    def __init__(self, *args):
        """Initialize the UnexpectedDataArguments exception.

        Args:
            *args: Variable length argument list.
        """
        super(UnexpectedDataArguments, self).__init__(args)


class UploadImageDataError(BaseCustomException):
    """Raised when there is an error during image data upload."""

    def __init__(self, *args):
        """Initialize the UploadImageDataError exception.

        Args:
            *args: Variable length argument list.
        """
        super(UploadImageDataError, self).__init__(args)


class ImageHasAttachmentError(BaseCustomException):
    """Raised when an operation is attempted on an image with attachments."""

    def __init__(self, *args):
        """Initialize the ImageHasAttachmentError exception.

        Args:
            *args: Variable length argument list.
        """
        super(ImageHasAttachmentError, self).__init__(args)


class ImageStatusError(BaseCustomException):
    """Raised when there is an error related to the image status."""

    def __init__(self, *args):
        """Initialize the ImageStatusError exception.

        Args:
            *args: Variable length argument list.
        """
        super(ImageStatusError, self).__init__(args)


class ValidateArgumentsError(BaseCustomException):
    """Raised when there is an error in validating arguments."""

    def __init__(self, *args):
        """Initialize the ValidateArgumentsError exception.

        Args:
            *args: Variable length argument list.
        """
        super(ValidateArgumentsError, self).__init__(args)


class StorageUnavailableException(BaseCustomException):
    """Raised when the storage is unavailable."""

    def __init__(self, *args):
        """Initialize the StorageUnavailableException exception.

        Args:
            *args: Variable length argument list.
        """
        super(StorageUnavailableException, self).__init__(args)


class ImageHasNotStorage(BaseCustomException):
    """Raised when an image does not have a corresponding storage."""

    def __init__(self, *args):
        """Initialize the ImageHasNotStorage exception.

        Args:
            *args: Variable length argument list.
        """
        super(ImageHasNotStorage, self).__init__(args)


class ImageHasSameAttachment(BaseCustomException):
    """Raised when an image has the same attachment already."""

    def __init__(self, *args):
        """Initialize the ImageHasSameAttachment exception.

        Args:
            *args: Variable length argument list.
        """
        super(ImageHasSameAttachment, self).__init__(args)


class ImageNameExistsException(BaseCustomException):
    """Raised when an image with the same name already exists."""

    def __init__(self, *args):
        """Initialize the ImageNameExistsException exception.

        Args:
            *args: Variable length argument list.
        """
        super(ImageNameExistsException, self).__init__(args)


class ImageDeletingError(BaseCustomException):
    """Raised when an error occurs during image deletion."""

    def __init__(self, *args):
        """Initialize the ImageDeletingError exception.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(args)
