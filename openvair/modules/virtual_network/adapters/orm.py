"""ORM mapping for the virtual network adapter.

This module defines the SQLAlchemy ORM mappings for virtual networks and
their associated port groups.

Classes:
    - PortGroup: ORM class for the port group table.
    - VirtualNetwork: ORM class for the virtual network table.

Functions:
    - start_mappers: Start the ORM mappings for virtual networks and port
        groups.
"""

import uuid

from sqlalchemy import (
    UUID,
    ARRAY,
    Text,
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column
from sqlalchemy.ext.mutable import MutableList


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class PortGroup(Base):
    """ORM class for the port group table."""

    __tablename__ = 'virtual_network_port_groups'

    port_group_name: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
    )
    is_trunk: Mapped[str] = mapped_column(String, nullable=True)
    tags: Mapped[list] = mapped_column(
        MutableList.as_mutable(ARRAY(Integer)),
        nullable=True,
    )
    virtual_network_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_networks.id'),
        primary_key=True,
        nullable=False,
    )

    virtual_network: Mapped['VirtualNetwork'] = relationship(
        'VirtualNetwork',
        back_populates='port_groups',
    )


class VirtualNetwork(Base):
    """ORM class for the virtual network table."""

    __tablename__ = 'virtual_networks'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    network_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    forward_mode: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    bridge: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    virtual_port_type: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    state: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    autostart: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    persistent: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    virsh_xml: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    port_groups: Mapped[list[PortGroup]] = relationship(
        'PortGroup',
        back_populates='virtual_network',
        uselist=True,
        lazy='selectin',
        cascade='all, delete-orphan',
    )
