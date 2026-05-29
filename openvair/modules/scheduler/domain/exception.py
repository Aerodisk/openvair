"""Domain-specific exceptions for the scheduler module.

This module defines exceptions related to cron job operations
within the domain layer.
"""

from openvair.modules.scheduler.shared.base_exceptions import (
    SchedulerDomainException as BaseSchedulerDomainException,
)


class SchedulerDomainException(BaseSchedulerDomainException):
    """Domain-layer base exception alias for requirements naming."""

    pass


class CronJobNotFound(SchedulerDomainException):
    """Raised when a specific cron job cannot be found."""
    pass


class InvalidCronExpression(SchedulerDomainException):
    """Raised when a cron expression has an invalid format."""
    pass


class CronTabReadException(SchedulerDomainException):
    """Raised when there is an error reading the system's crontab."""
    pass


class CronTabWriteException(SchedulerDomainException):
    """Raised when there is an error writing to the system's crontab."""
    pass


class CronDaemonException(SchedulerDomainException):
    """Raised for issues related to the cron daemon/service itself."""
    pass
