"""SQLAlchemy ORM models for the template module.

This module defines database models for the template module using SQLAlchemy
ORM.

Classes:
    Template: ORM class representing a template.
"""

import uuid
import datetime

from sqlalchemy import Text, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    """Base class for ORM mappings in the template module."""

    pass


class Template(Base):
    """ORM class representing a template.

    Attributes:
        id: Unique identifier of the template.
        name: Unique name of the template.
        description: Optional description.
        path: Filesystem path to the qcow2 file stored in storage.
        storage_id: Identifier of the storage where the template is located.
        is_backing: Flag indicating whether the template is a backing file.
        created_at: Timestamp when the template was created.

    """

    __tablename__ = 'templates'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    storage_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now(),
    )
    is_backing: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
