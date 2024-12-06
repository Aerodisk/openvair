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

from sqlalchemy import String, Boolean
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column,
)
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class User(Base):
    """Placeholder class for user ORM mapping.

    This class is used as a placeholder for ORM mapping with SQLAlchemy.
    It does not contain any logic or attributes.
    """

    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
