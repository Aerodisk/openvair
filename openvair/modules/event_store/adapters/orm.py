"""Module for defining the SQLAlchemy ORM mappings for event-related data.

This module sets up the metadata and registry for SQLAlchemy, defines the
schema for the `events` table, and maps the `Events` class to this table.

Classes:
    Events: A class representing the events in the system.

Functions:
    start_mappers: Function to start the mapping of classes to tables.
"""

import contextlib

from sqlalchemy import Text, Table, Column, String, Integer, DateTime, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import registry
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

events = Table(
    'events',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('module', String(40)),
    Column('object_id', postgresql.UUID(as_uuid=True)),
    Column('user_id', postgresql.UUID(as_uuid=True)),
    Column('event', String(50), default=''),
    Column('timestamp', DateTime, default=func.now()),
    Column('information', Text),
)


class Events:
    """A class representing an event in the system.

    This class is mapped to the `events` table, which stores information about
    various events occurring within the system.
    """

    pass


def start_mappers() -> None:
    """Start the mapping of classes to tables.

    This function suppresses any SQLAlchemy errors that may occur during the
    mapping process and maps the `Events` class to the `events` table.
    """
    with contextlib.suppress(SQLAlchemyError):
        mapper_registry.map_imperatively(Events, events)
