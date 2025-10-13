"""SQLAlchemy ORM mappings for notifications.

This module defines the ORM mappings and metadata for the notifications table.
It also provides a function to start the ORM mappers.
"""

import uuid
import datetime

from sqlalchemy import UUID, ARRAY, TIMESTAMP, String, MetaData, func
from sqlalchemy.orm import Mapped, DeclarativeBase, registry, mapped_column

# Metadata and mapper registry for SQLAlchemy
metadata = MetaData()
mapper_registry = registry(metadata=metadata)


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class Notification(Base):
    """Domain model for a notification."""

    __tablename__ = 'notifications'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    create_datetime: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=func.now(),
        nullable=True,
    )
    msg_type: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    subject: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    recipients: Mapped[list] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
    message: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
