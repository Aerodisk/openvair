"""Module for defining ORM mappings for storage-related tables.

This module defines the ORM mappings for storage-related tables using
SQLAlchemy. It includes the definition of tables for storing storage
information and extra specifications, as well as classes representing
these tables.

Classes:
    Storage: Represents the main storage table.
    StorageExtraSpecs: Represents key-value pairs of extra specifications
        for storage.

Functions:
    start_mappers: Configures ORM mappings for the storage-related tables.
"""

import uuid
from typing import List

from sqlalchemy import (
    UUID,
    Text,
    String,
    Boolean,
    Integer,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    relationship,
    mapped_column,
)


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class Storage(Base):
    """Represents the `storages` table in the database.

    This class maps to the `storages` table, which stores general information
    about each storage, such as its type, status, and size.
    """

    __tablename__ = 'storages'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    storage_type: Mapped[str] = mapped_column(String(30), nullable=False)
    initialized: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    information: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    size: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=True,
    )
    available: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(
        UUID(),
        nullable=True,
    )
    extra_specs: Mapped[List['StorageExtraSpecs']] = relationship(
        'StorageExtraSpecs', back_populates='storage', uselist=True
    )


class StorageExtraSpecs(Base):
    """Represents the `storage_extra_specs` table in the database.

    This table stores key-value pairs of extra specifications for each storage.
    The `StorageExtraSpecs` class maps to this table.

    Example:
        If a storage has specifications like IP address and path, the table
        will store them as follows:

        id    |    key    |    value    |    storage_id
        -----------------------------------------------
        1     |    ip     |   0.0.0.0   |    UUID(1)
        2     |   path    |  /nfs/data  |    UUID(1)
    """

    __tablename__ = 'storage_extra_specs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    value: Mapped[str] = mapped_column(
        String(155),
        nullable=True,
    )
    storage_id: Mapped[uuid.UUID] = mapped_column(
        'storage_id',
        UUID(),
        ForeignKey('storages.id'),
        nullable=True,
    )

    storage: Mapped[Storage] = relationship(
        'Storage', back_populates='extra_specs'
    )
