"""Module defining SQLAlchemy table mappings and relationships for image module.

This module defines the SQLAlchemy table structures and mappings for the `Image`
and `ImageAttachVM` classes, which represent images and their attachments to
virtual machines (VMs). It also includes a function to initialize the mappings.

Tables:
    images: Table for storing image metadata and associated information.
    image_attach_vm: Table for storing relationships between images and VMs.

Classes:
    Image: Represents an image in the system.
    ImageAttachVM: Represents the association between an image and a VM.

Functions:
    start_mappers: Configures the mappings between the `Image` and
        `ImageAttachVM` classes and their corresponding database tables.
"""

import uuid

from sqlalchemy import (
    Text,
    Table,
    Column,
    String,
    Integer,
    MetaData,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import registry, relationship
from sqlalchemy.dialects import postgresql

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

images = Table(
    'images',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('name', String(40)),
    Column('user_id', postgresql.UUID(as_uuid=True)),
    Column('size', BigInteger),
    Column('path', String(255), default=''),
    Column('status', String(20)),
    Column('information', Text),
    Column('description', String(255)),
    Column('storage_id', postgresql.UUID(as_uuid=True)),
    Column('storage_type', String(30), default=''),
)


image_attach_vm = Table(
    'image_attach_vm',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('image_id', postgresql.UUID(as_uuid=True), ForeignKey('images.id')),
    Column('vm_id', postgresql.UUID(as_uuid=True)),
    Column('user_id', postgresql.UUID(as_uuid=True)),
    Column('target', String(50)),
)


class Image:
    """Represents an image in the system.

    This class corresponds to a record in the `images` table, containing
    metadata and associated information about an image.
    """

    pass


class ImageAttachVM:
    """Represents the association between an image and a VM.

    This class corresponds to a record in the `image_attach_vm` table,
    representing the relationship between an image and a virtual machine
    (VM), including details such as the target device.
    """

    pass


def start_mappers() -> None:
    """Configures the mappings between the classes and their respective tables.

    This function sets up the SQLAlchemy mappings between the `Image` and
    `ImageAttachVM` classes and their corresponding database tables (`images`
    and `image_attach_vm`, respectively). It also defines the relationships
    between these entities.

    Returns:
        None
    """
    mapper_registry.map_imperatively(
        Image,
        images,
        properties={
            'attachments': relationship(
                ImageAttachVM, backref='image', uselist=True
            ),
        },
    )
    mapper_registry.map_imperatively(ImageAttachVM, image_attach_vm)
