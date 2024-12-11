"""Module for custom exceptions in the restic adapters."""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class ResticError(BaseCustomException):
    """Base errro class for error in restic adapter"""

    def __init__(self, message: str, *args: Any):  # noqa: ANN401
        """Initialize ResticAdapterException"""
        super().__init__(message, args)


class ResticExecutorError(ResticError):
    """Raises when execution failed"""

    ...


class ResticInitRepoError(ResticError):
    """Raises when getting error while initialize restic repository"""

    ...
