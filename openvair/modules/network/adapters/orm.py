"""ORM mapping for network module entities.

This module defines SQLAlchemy ORM mappings for network interfaces and
their associated extra specifications. It sets up the necessary database
tables and relationships.

Classes:
    Interface: ORM class representing a network interface.
    InterfaceExtraSpec: ORM class representing extra specifications for
        a network interface.

Functions:
    start_mappers: Initializes ORM mappings for network-related tables.
"""

import uuid

from sqlalchemy import UUID, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class Interface(Base):
    """Represents a network interface."""

    __tablename__ = 'interfaces'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    mac: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    ip: Mapped[str] = mapped_column(
        String(40),
        nullable=True,
    )
    netmask: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    gateway: Mapped[str] = mapped_column(
        String(40),
        nullable=True,
    )
    inf_type: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    mtu: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    speed: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    power_state: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default='available'
    )

    extra_specs: Mapped[list['InterfaceExtraSpec']] = relationship(
        'InterfaceExtraSpec',
        back_populates='interface',
        uselist=True,
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class InterfaceExtraSpec(Base):
    """Represents extra specifications for a network interface."""

    __tablename__ = 'interface_extra_specs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    value: Mapped[str] = mapped_column(
        String(155),
        nullable=True,
    )
    interface_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('interfaces.id'),
        nullable=True,
    )

    interface: Mapped[Interface] = relationship(
        'Interface',
        back_populates='extra_specs',
    )
