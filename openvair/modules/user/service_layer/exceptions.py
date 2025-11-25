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

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class UserCredentialsException(BaseCustomException):
    """Raised when there is an issue with user credentials."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UserCredentialsException."""
        super().__init__(message, *args)


class UserExistsException(BaseCustomException):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UserExistsException."""
        super().__init__(message, *args)


class UnexpectedData(BaseCustomException):
    """Raised for unexpected data encountered during processing."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UnexpectedData exception."""
        super().__init__(message, *args)


class UserDoesNotExist(BaseCustomException):
    """Raised when attempting to access a user that does not exist."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the UserDoesNotExist exception."""
        super().__init__(message, *args)


class NotSuperUser(BaseCustomException):
    """Raised when a non-superuser attempts a superuser action."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the NotSuperUser exception."""
        super().__init__(message, *args)


class WrongUserIdProvided(BaseCustomException):
    """Raised when an invalid user ID is provided."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the WrongUserIdProvided exception."""
        super().__init__(message, *args)


class PasswordVerifyException(BaseException):
    """Raised when get error while verifying password"""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the PasswordVerifyException."""
        super().__init__(message, *args)
