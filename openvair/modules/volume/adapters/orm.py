"""ORM mappings for the volume module.

This module defines the SQLAlchemy ORM mappings for the volume-related database
tables. It includes mappings for volumes and their attachments to virtual
machines.

Classes:
    Volume: ORM class representing a volume.
    VolumeAttachVM: ORM class representing the attachment of a volume to a
        virtual machine.

Functions:
    start_mappers: Initialize the ORM mappings for the volume-related tables.
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

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

volumes = Table(
    'volumes',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('name', String(40)),
    Column('user_id', postgresql.UUID(as_uuid=True)),
    Column('format', String(10)),
    Column('size', BigInteger),
    Column('used', BigInteger),
    Column('status', String(20)),
    Column('information', Text),
    Column('path', String(255), default=''),
    Column('description', String(255)),
    Column('storage_id', postgresql.UUID(as_uuid=True)),
    Column('storage_type', String(30), default=''),
    Column('read_only', Boolean(), default=False),
)


volume_attach_vm = Table(
    'volume_attach_vm',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column(
        'volume_id', postgresql.UUID(as_uuid=True), ForeignKey('volumes.id')
    ),
    Column('vm_id', postgresql.UUID(as_uuid=True)),
    Column('user_id', postgresql.UUID(as_uuid=True)),
    Column('target', String(50)),
)


class Volume:
    """ORM class representing a volume."""

    pass


class VolumeAttachVM:
    """ORM class representing the attachment volume to a virtual machine."""

    pass


def start_mappers() -> None:
    """Initialize the ORM mappings for the volume-related tables.

    This function sets up the ORM mappings between the Volume and VolumeAttachVM
    classes and their corresponding database tables.
    """
    mapper_registry.map_imperatively(
        Volume,
        volumes,
        properties={
            'attachments': relationship(
                VolumeAttachVM, backref='volume', uselist=True
            ),
        },
    )
    mapper_registry.map_imperatively(VolumeAttachVM, volume_attach_vm)
