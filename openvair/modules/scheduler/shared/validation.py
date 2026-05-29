"""Shared validation helpers for scheduler job payloads."""

from typing import Optional

from crontab import CronSlices

MIN_CRON_FIELDS = 5


def enforce_minute_granularity(cron_value: str) -> str:
    """Ensure cron expression uses exactly five fields (minute granularity)."""
    parts = cron_value.split()
    if len(parts) != MIN_CRON_FIELDS:
        msg = (
            'Cron expression must contain exactly 5 fields '
            '(minute granularity)'
        )
        raise ValueError(msg)
    return cron_value


def validate_cron_schedule(value: str) -> str:
    """Validate non-empty cron expression syntax."""
    if not value or not value.strip():
        msg = 'Cron schedule cannot be empty or whitespace'
        raise ValueError(msg)
    stripped = value.strip()
    if not CronSlices.is_valid(stripped):
        msg = f'Invalid cron expression: {value}'
        raise ValueError(msg)
    return enforce_minute_granularity(stripped)


def validate_optional_cron_schedule(value: Optional[str]) -> Optional[str]:
    """Validate cron expression when the field is present."""
    if value is None:
        return value
    return validate_cron_schedule(value)


def validate_non_empty_name(value: str) -> str:
    """Ensure job name is not empty or whitespace-only."""
    if not value or not value.strip():
        msg = 'Field cannot be empty or whitespace'
        raise ValueError(msg)
    return value.strip()


def validate_optional_name(value: Optional[str]) -> Optional[str]:
    """Validate optional job name."""
    if value is not None and not value.strip():
        msg = 'Field cannot be only whitespace'
        raise ValueError(msg)
    return value.strip() if value else value
