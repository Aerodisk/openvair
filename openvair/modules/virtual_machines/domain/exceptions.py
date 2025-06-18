"""Exception classes for the virtual machine domain layer.

This module defines custom exceptions used in the virtual machine domain layer,
particularly for handling errors related to virtual machine operations.

Classes:
    GraphicPortNotFoundInXmlException: Exception raised when getting error while
        searching port of graphic in vm xml
    GraphicTypeNotFoundInXmlException: Exception raised when getting error while
        searching type of graphic in vm xml
    VNCSessionError: Exception raised for errors related to VNC session
        management.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class GraphicPortNotFoundInXmlException(BaseCustomException):
    """Raised when getting error while searching port of graphic in vm xml"""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the GraphicPortNotFoundInXmlException exception."""
        super().__init__(message, *args)


class GraphicTypeNotFoundInXmlException(BaseCustomException):
    """Raised when getting error while searching type of graphic in vm xml"""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the GraphicPortNotFoundInXmlException exception."""
        super().__init__(message, *args)


class VNCSessionError(BaseCustomException):
    """Exception raised for errors related to VNC session management."""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the VNCSessionError with a message."""
        super().__init__(message, *args)


class SnapshotError(BaseCustomException):
    """Raised when getting error while operating snapshots in Libvirt API"""

    def __init__(self, message: str, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the SnapshotCreationError with a message."""
        super().__init__(message, *args)
