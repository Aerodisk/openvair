"""SQLAlchemy ORM mappings for notifications.

This module defines the ORM mappings and metadata for the notifications table.
It also provides a function to start the ORM mappers.
"""

import uuid

from sqlalchemy import ARRAY, TIMESTAMP, Table, Column, String, MetaData, func
from sqlalchemy.orm import registry
from sqlalchemy.dialects import postgresql

# Metadata and mapper registry for SQLAlchemy
metadata = MetaData()
mapper_registry = registry(metadata=metadata)

# Table definition for notifications
notifications = Table(
    'notifications',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('create_datetime', TIMESTAMP, default=func.now()),
    Column('msg_type', String(30)),
    Column('subject', String(30)),
    Column('recipients', ARRAY(String)),
    Column('message', String(255)),
    Column('status', String(255)),
)


class Notification:
    """Domain model for a notification."""

    pass


def start_mappers() -> None:
    """Start the ORM mappers.

    This function initializes the ORM mappers for the Notification class.
    """
    mapper_registry.map_imperatively(Notification, notifications)
