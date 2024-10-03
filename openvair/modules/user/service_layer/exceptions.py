"""Exception classes for the user service layer.

This module defines custom exceptions used in the user service layer. These
exceptions handle specific error conditions that may arise during user
operations, such as invalid credentials, user existence issues, or unauthorized
actions.

Classes:
    UserCredentialsException: Raised when there is an issue with user
        credentials.
    UserExistsException: Raised when attempting to create a user that already
        exists.
    UnexpectedData: Raised for unexpected data encountered during processing.
    UserDoesNotExist: Raised when attempting to access a user that does not
        exist.
    NotSuperUser: Raised when an action requiring superuser privileges is
        attempted by a non-superuser.
    WrongUserIdProvided: Raised when an invalid user ID is provided.
"""

from openvair.modules.tools.base_exception import BaseCustomException


class UserCredentialsException(BaseCustomException):
    """Raised when there is an issue with user credentials."""

    def __init__(self, *args):
        """Initialize the UserCredentialsException.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class UserExistsException(BaseCustomException):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, *args):
        """Initialize the UserExistsException.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class UnexpectedData(BaseCustomException):
    """Raised for unexpected data encountered during processing."""

    def __init__(self, *args):
        """Initialize the UnexpectedData exception.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class UserDoesNotExist(BaseCustomException):
    """Raised when attempting to access a user that does not exist."""

    def __init__(self, *args):
        """Initialize the UserDoesNotExist exception.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class NotSuperUser(BaseCustomException):
    """Raised when a non-superuser attempts a superuser action."""

    def __init__(self, *args):
        """Initialize the NotSuperUser exception.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)


class WrongUserIdProvided(BaseCustomException):
    """Raised when an invalid user ID is provided."""

    def __init__(self, *args):
        """Initialize the WrongUserIdProvided exception.

        Args:
            *args: Variable length argument list.
        """
        super().__init__(*args)
