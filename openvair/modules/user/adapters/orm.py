"""ORM mappings and schema definitions for the user module.

This module defines the SQLAlchemy ORM mappings and schema for the user
management system. It includes the definition of the `users` table and
the `User` class for ORM operations.

Classes:
    User: Placeholder class for user ORM mapping.

Functions:
    start_mappers: Maps the `User` class to the `users` table.
"""

import uuid

from sqlalchemy import Table, Column, String, Boolean, MetaData
from sqlalchemy.orm import registry
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()
mapper_registry = registry(metadata=metadata)


users = Table(
    'users',
    mapper_registry.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('username', String(30), unique=True),
    Column('email', String(255), unique=True),
    Column('is_superuser', Boolean, default=False),
    Column('hashed_password', String(255)),
)


class User:
    """Placeholder class for user ORM mapping.

    This class is used as a placeholder for ORM mapping with SQLAlchemy.
    It does not contain any logic or attributes.
    """
    pass


def start_mappers() -> None:
    """Maps the `User` class to the `users` table.

    This function is responsible for setting up the ORM mappings for the
    `User` class, associating it with the `users` table in the database.
    """
    mapper_registry.map_imperatively(User, users)
