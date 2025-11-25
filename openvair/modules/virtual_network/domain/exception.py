"""Module for custom exceptions in the virtual network domain.

This module defines custom exceptions related to port groups and network
definition in the virtual network domain.

Classes:
    - PortGroupException: Exception raised when an error occurs with a port
        group.
    - VirshDefineNetworkException: Exception raised when an error occurs
        during the definition of a network with Virsh.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class PortGroupException(BaseCustomException):
    """Exception raised when an error occurs with a port group."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the PortGroupException."""
        super().__init__(message, *args)


class VirshDefineNetworkException(BaseCustomException):
    """Exception raised when an error occurs during the definition with Virsh.

    Attributes:
        args (Tuple): The arguments passed to the exception.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the VirshDefineNetworkException."""
        super().__init__(message, *args)
