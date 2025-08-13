"""Common Pydantic-level types and aliases used across DTOs and API schemas.

This module must not depend on SQLAlchemy or application modules.
"""

from datetime import datetime, timezone

from pydantic import AfterValidator, PlainSerializer
from typing_extensions import Annotated


def _ensure_aware_utc(dt: datetime) -> datetime:
    """Ensure a datetime object is timezone-aware in UTC.

    This function is used as a post-validation step in Pydantic models.
    If the provided datetime is naive (has no timezone information), it will
    be set to UTC. If it is already timezone-aware, it will be converted to UTC.

    Args:
        dt (datetime): The datetime object to validate and adjust.

    Returns:
        datetime: A timezone-aware datetime object in UTC.
    """
    return (
        dt.replace(tzinfo=timezone.utc)
        if dt.tzinfo is None
        else dt.astimezone(timezone.utc)
    )


def _iso_utc(dt: datetime) -> str:
    """Serialize a datetime object in UTC to ISO 8601 format.

    This function ensures that the datetime is represented as a string in
    ISO 8601 format, replacing the "+00:00" suffix with "Z" for UTC.

    Args:
        dt (datetime): The UTC datetime object to serialize.

    Returns:
        str: The ISO 8601 string representation of the datetime in UTC.
    """
    return dt.isoformat().replace('+00:00', 'Z')


UTCDateTime = Annotated[
    datetime,  # ← the base type is a regular datetime
    AfterValidator(_ensure_aware_utc),  # ← cast to UTC-aware
    PlainSerializer(_iso_utc, return_type=str),
]
