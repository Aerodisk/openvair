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

from sqlalchemy import Text, String, Integer, DateTime, text
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
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
    module: Mapped[str] = mapped_column(String(40), nullable=False)
    object_id: Mapped[uuid.UUID] = mapped_column(postgresql.UUID(as_uuid=True))
    user_id: Mapped[uuid.UUID] = mapped_column(postgresql.UUID(as_uuid=True))
    event: Mapped[str] = mapped_column(String(50), default='', nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),  # TIMESTAMP WITH TIME ZONE
        server_default=text("TIMEZONE('UTC', NOW())"),  # explicitly fixes UTC
        nullable=False,
    )
    information: Mapped[str] = mapped_column(Text, nullable=False)
