"""Base exceptions for the scheduler module.

This module defines common exceptions used across the scheduler module.

Classes:
    - BaseSchedulerServiceLayerException: Base exception for service layer
        errors.
    - SchedulerDomainException: Base exception for domain-level errors.
"""

from openvair.abstracts.base_exception import BaseCustomException


class SchedulerDomainException(BaseCustomException):
    """Base exception for errors occurring in the scheduler domain."""

    ...
