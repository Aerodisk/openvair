"""Exceptions that may occur during the cloning process.

Classes:
    NoAvailableNameForClone: Raised when the maximum clone index may be exceeded
    during the cloning process.
    CloneNameTooLong: Raised when the clone's name exceeds the maximum allowed
    length.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NoAvailableNameForClone(BaseCustomException):
    """Raised when there is no available name for a copy."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the NoAvailableNameForClone with a message."""
        super().__init__(message, *args)

class CloneNameTooLong(BaseCustomException):
    """Raised when the name of the object's copy is too long."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the CloneNameTooLong with a message."""
        super().__init__(message, *args)
