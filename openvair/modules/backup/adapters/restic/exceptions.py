"""Module for custom exceptions in the backup adapters.

Classes:
    BackupDomainException: base exception class for exceptions in backup domain
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class ResticException(BaseCustomException):
    """Base exception class for exceptions in ResticAdapter"""

    def __init__(self, message: str, *args: Any):  # noqa: ANN401
        """Initialize ResticAdapterException"""
        super().__init__(message, args)


class ResticExecutorException(ResticException):
    """Base exception class for exceptions in ResticAdapter"""

    def __init__(self, message: str, *args: Any):  # noqa: ANN401
        """Initialize ResticExecutorException"""
        super().__init__(message, args)
