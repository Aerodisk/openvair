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

from sqlalchemy import (
    Text,
    Table,
    Column,
    String,
    Boolean,
    Integer,
    MetaData,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import registry, relationship
from sqlalchemy.dialects import postgresql

# Metadata and registry for SQLAlchemy
metadata = MetaData()
mapper_registry = registry(metadata=metadata)

# Definition of the `storages` table
storages = Table(
    'storages',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('name', String(60)),
    Column('description', String(255)),
    Column('storage_type', String(30), nullable=False),
    Column('initialized', Boolean, default=False),
    Column('status', String(30), nullable=False),
    Column('information', Text),
    Column('size', BigInteger, default=0),
    Column('available', BigInteger, default=0),
    Column('user_id', postgresql.UUID(as_uuid=True)),
)

# Definition of the `storage_extra_specs` table
storage_extra_specs = Table(
    'storage_extra_specs',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('key', String(60)),
    Column('value', String(155)),
    Column(
        'storage_id', postgresql.UUID(as_uuid=True), ForeignKey('storages.id')
    ),
)


class Storage:
    """Represents the `storages` table in the database.

    This class maps to the `storages` table, which stores general information
    about each storage, such as its type, status, and size.
    """

    pass


class StorageExtraSpecs:
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

    pass


def start_mappers() -> None:
    """Configure ORM mappings for storage-related tables.

    This function maps the `Storage` and `StorageExtraSpecs` classes to
    their corresponding tables in the database.
    """
    mapper_registry.map_imperatively(
        Storage,
        storages,
        properties={
            'extra_specs': relationship(
                StorageExtraSpecs, backref='storage', uselist=True
            ),
        },
    )
    mapper_registry.map_imperatively(StorageExtraSpecs, storage_extra_specs)
