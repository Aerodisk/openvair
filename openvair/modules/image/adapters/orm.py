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
"""

import uuid
from typing import List, Optional

from sqlalchemy import (
    UUID,
    Text,
    String,
    Integer,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column
from sqlalchemy.dialects import postgresql


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class Image(Base):
    """Represents an image in the system.

    This class corresponds to a record in the `images` table, containing
    metadata and associated information about an image.
    """

    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[Optional[str]] = mapped_column(String(40))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        postgresql.UUID(as_uuid=True)
    )
    size: Mapped[Optional[int]] = mapped_column(BigInteger)
    path: Mapped[Optional[str]] = mapped_column(String(255), default='')
    status: Mapped[Optional[str]] = mapped_column(String(20))
    information: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    storage_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        postgresql.UUID(as_uuid=True)
    )
    storage_type: Mapped[Optional[str]] = mapped_column(String(30), default='')

    attachments: Mapped[List['ImageAttachVM']] = relationship(
        'ImageAttachVM', back_populates='image', uselist=True, lazy='selectin',
    )


class ImageAttachVM(Base):
    """Represents the association between an image and a VM.

    This class corresponds to a record in the `image_attach_vm` table,
    representing the relationship between an image and a virtual machine
    (VM), including details such as the target device.
    """

    __tablename__ = 'image_attach_vm'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('images.id'), nullable=True
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(UUID(), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(), nullable=True)
    target: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    image: Mapped[Image] = relationship('Image', back_populates='attachments')
