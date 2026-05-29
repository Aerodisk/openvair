"""Base exceptions for the scheduler module.

This module defines common exceptions used across the scheduler module.

Classes:
    - BaseSchedulerServiceLayerException: Base exception for service layer
        errors.
    - SchedulerDomainException: Base exception for domain-level errors.
"""

from typing import Optional

from openvair.abstracts.base_exception import BaseCustomException


class SchedulerDomainException(BaseCustomException):
    """Base exception for errors occurring in the scheduler domain."""

    ...

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
