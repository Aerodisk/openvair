"""Exception classes for virtual network operations in the service layer.

This module defines custom exceptions related to virtual network operations,
which are used throughout the service layer.

Classes:
    - DataBaseVirtualNetworkException: Raised when a database-related error
        occurs in virtual network operations.
    - VirtualNetworkAlreadyExist: Raised when a virtual network already exists
        and cannot be created.
    - VirtualNetworkDoesNotExist: Raised when a requested virtual network does
        not exist.
    - PortGroupException: Raised when an error occurs related to port groups in
        a virtual network.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class DataBaseVirtualNetworkException(BaseCustomException):
    """Raised when a database error occurs in virtual network operations."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class VirtualNetworkAlreadyExist(BaseCustomException):
    """Raised when a virtual network already exists and cannot be created."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class VirtualNetworkDoesNotExist(BaseCustomException):
    """Raised when a requested virtual network does not exist."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class PortGroupException(BaseCustomException):
    """Raised when an error occurs related to port groups in virtual network."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)
