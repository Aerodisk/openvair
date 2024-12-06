"""Exception classes for ISCSI operations."""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class ISCSIGetIQNException(BaseCustomException):
    """Exception raised when getting ISCSI IQN fails."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class ISCSIIqnNotFoundException(BaseCustomException):
    """Exception raised when ISCSI IQN is not found"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class ISCSIDiscoveryError(BaseCustomException):
    """Exception raised during ISCSI discovery error."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class ISCSILoginError(BaseCustomException):
    """Exception raised during ISCSI login error."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class ISCSILogoutError(BaseCustomException):
    """Exception raised during ISCSI logout error."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)


class LipScanError(BaseCustomException):
    """Exception raised during LIP scan error."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the exception with optional arguments."""
        super().__init__(message, *args)
