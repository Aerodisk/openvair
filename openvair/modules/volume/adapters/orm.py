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
    """Base class for inheritance volumes and attachments volumes."""

    pass


class Volume(Base):
    """ORM class representing a volume."""

    __tablename__ = 'volumes'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(40),
        nullable=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )
    format: Mapped[str] = mapped_column(
        String(10),
        nullable=True,
    )
    size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
    )
    used: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    information: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    path: Mapped[str] = mapped_column(
        String(255),
        default='',
        nullable=True,
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    storage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )
    storage_type: Mapped[str] = mapped_column(
        String(30),
        default='',
        nullable=True,
    )
    read_only: Mapped[bool] = mapped_column(
        Boolean(),
        default=False,
        nullable=True,
    )

    attachments: Mapped[List['VolumeAttachVM']] = relationship(
        'VolumeAttachVM',
        back_populates='volume',
        uselist=True,
    )


class VolumeAttachVM(Base):
    """ORM class representing the attachment volume to a virtual machine."""

    __tablename__ = 'volume_attach_vm'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    volume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('volumes.id'),
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )
    target: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    volume: Mapped[Volume] = relationship(
        'Volume',
        back_populates='attachments',
    )
