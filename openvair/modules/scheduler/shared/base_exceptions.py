"""Base exceptions for the scheduler module."""

from typing import Optional

from openvair.abstracts.base_exception import BaseCustomException


class BaseSchedulerServiceLayerException(BaseCustomException):
    """Exception raised for errors occurring in the service layer."""

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        job_id: Optional[int] = None,
        details: Optional[str] = None,
    ) -> None:
        """Initialize base scheduler service layer exception."""
        super().__init__(message or self.__class__.__name__)
        self.job_id = job_id
        self.details = details
