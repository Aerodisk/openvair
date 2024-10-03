"""Exception classes for ISCSI operations."""

from openvair.modules.tools.base_exception import BaseCustomException


class ISCSIGetIQNException(BaseCustomException):
    """Exception raised when getting ISCSI IQN fails."""
    def __init__(self, *args):
        """Initialize the exception with optional arguments."""
        super().__init__(*args)


class ISCSIIqnNotFoundException(BaseCustomException):
    """Exception raised when ISCSI IQN is not found"""
    def __init__(self, *args):
        """Initialize the exception with optional arguments."""
        super().__init__(*args)


class ISCSIDiscoveryError(BaseCustomException):
    """Exception raised during ISCSI discovery error."""
    def __init__(self, *args):
        """Initialize the exception with optional arguments."""
        super().__init__(*args)


class ISCSILoginError(BaseCustomException):
    """Exception raised during ISCSI login error."""
    def __init__(self, *args):
        """Initialize the exception with optional arguments."""
        super().__init__(*args)


class ISCSILogoutError(BaseCustomException):
    """Exception raised during ISCSI logout error."""
    def __init__(self, *args):
        """Initialize the exception with optional arguments."""
        super().__init__(*args)


class LipScanError(BaseCustomException):
    """Exception raised during LIP scan error."""
    def __init__(self, *args):
        """Initialize the exception with optional arguments."""
        super().__init__(*args)
