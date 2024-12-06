"""Module for defining the SQLAlchemy ORM mappings for event-related data.

This module sets up the metadata and registry for SQLAlchemy, defines the
schema for the `events` table, and maps the `Events` class to this table.

Classes:
    Events: A class representing the events in the system.

Functions:
    start_mappers: Function to start the mapping of classes to tables.
"""

import uuid
import datetime
from typing import Optional

from sqlalchemy import Text, String, Integer, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class Events(Base):
    """A class representing an event in the system.

    This class is mapped to the `events` table, which stores information about
    various events occurring within the system.
    """

    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
    )
    module: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    object_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        postgresql.UUID(as_uuid=True)
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        postgresql.UUID(as_uuid=True)
    )
    event: Mapped[Optional[str]] = mapped_column(
        String(50), default='', nullable=True
    )
    timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=True,
    )
    information: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
