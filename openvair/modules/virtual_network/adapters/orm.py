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
    ARRAY,
    Text,
    Table,
    Column,
    String,
    Integer,
    MetaData,
    ForeignKey,
)
from sqlalchemy.orm import registry, relationship
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import MutableList

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

port_groups = Table(
    'virtual_network_port_groups',
    mapper_registry.metadata,
    Column('port_group_name', String, primary_key=True, nullable=False),
    Column('is_trunk', String),
    Column('tags', MutableList.as_mutable(ARRAY(Integer))),
    Column(
        'virtual_network_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_networks.id'),
        primary_key=True,
        nullable=False,
    ),
)

virtual_networks = Table(
    'virtual_networks',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('network_name', String),
    Column('forward_mode', String),
    Column('bridge', String),
    Column('virtual_port_type', String),
    Column('state', String),
    Column('autostart', String),
    Column('persistent', String),
    Column('virsh_xml', Text),
)


class PortGroup:
    """ORM class for the port group table."""

    pass


class VirtualNetwork:
    """ORM class for the virtual network table."""

    pass


def start_mappers() -> None:
    """Start the ORM mappings for virtual networks and port groups."""
    mapper_registry.map_imperatively(
        VirtualNetwork,
        virtual_networks,
        properties={
            'port_groups': relationship(
                PortGroup,
                backref='virtual_network',
                uselist=True,
                cascade='all, delete-orphan',
            )
        },
    )

    mapper_registry.map_imperatively(
        PortGroup,
        port_groups,
    )
