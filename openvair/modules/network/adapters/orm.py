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

from sqlalchemy import Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import registry, relationship
from sqlalchemy.dialects import postgresql

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

interfaces = Table(
    'interfaces',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('name', String(30)),
    Column('mac', String(20)),
    Column('ip', String(40)),
    Column('netmask', Integer),
    Column('gateway', String(40)),
    Column('inf_type', String(20)),
    Column('mtu', Integer),
    Column('speed', Integer),
    Column('power_state', String(20), nullable=False),
    Column('status', String(20), nullable=False, default='available'),
)

interface_extra_specs = Table(
    'interface_extra_specs',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('key', String(60)),
    Column('value', String(155)),
    Column(
        'interface_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('interfaces.id'),
    ),
)


class Interface:
    """Represents a network interface."""

    pass


class InterfaceExtraSpec:
    """Represents extra specifications for a network interface."""

    pass


def start_mappers() -> None:
    """Initialize ORM mappings for network-related tables.

    This function sets up the SQLAlchemy mappings for the Interface and
    InterfaceExtraSpec tables and defines the relationships between them.
    """
    mapper_registry.map_imperatively(
        Interface,
        interfaces,
        properties={
            'extra_specs': relationship(
                InterfaceExtraSpec,
                backref='interface',
                uselist=True,
                cascade='all, delete-orphan',
            ),
        },
    )
    mapper_registry.map_imperatively(InterfaceExtraSpec, interface_extra_specs)
