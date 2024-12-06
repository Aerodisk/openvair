"""Custom exceptions for ISCSI and Fibre Channel operations.

This module defines several custom exception classes used throughout the
application to handle specific errors that may occur during ISCSI and
Fibre Channel operations.

Exceptions:
    ISCSILoginException: Raised during the ISCSI login process.
    ISCSILogoutException: Raised during the ISCSI logout process.
    ISCSIIqnGetException: Raised when retrieving the ISCSI IQN.
    FibreChannelLipScanException: Raised during the Fibre Channel LIP scan
        process.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class ISCSILoginException(BaseCustomException):
    """Exception raised during the ISCSI login process."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ISCSILoginException with the given arguments."""
        super().__init__(message, *args)


class ISCSILogoutException(BaseCustomException):
    """Exception raised during the ISCSI logout process."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ISCSILogoutException with the given arguments."""
        super().__init__(message, *args)


class ISCSIIqnGetException(BaseCustomException):
    """Exception raised when retrieving the ISCSI IQN."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ISCSIIqnGetException with the given arguments."""
        super().__init__(message, *args)


class FibreChannelLipScanException(BaseCustomException):
    """Exception raised during the Fibre Channel LIP scan process."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize FibreChannelLipScanException with the given arguments."""
        super().__init__(message, *args)
