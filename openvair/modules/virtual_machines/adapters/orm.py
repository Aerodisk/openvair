"""Module for ORM mappings related to virtual machines.

This module defines the ORM mappings for various entities associated with
virtual machines, including CPU information, operating system details, disks,
virtual interfaces, protocol graphic interfaces, and RAM. It uses SQLAlchemy
to define table schemas and relationships between these entities.

Tables:
    virtual_machines: Table containing virtual machine details.
    cpu_info: Table containing CPU information for virtual machines.
    os: Table containing operating system details for virtual machines.
    disk: Table containing disk information for virtual machines.
    virtual_interface: Table containing network interface information.
    protocol_graphic_interface: Table containing graphic interface protocol
        details.
    ram: Table containing RAM information for virtual machines.

Classes:
    VirtualMachines: ORM class mapped to the `virtual_machines` table.
    CpuInfo: ORM class mapped to the `cpu_info` table.
    Os: ORM class mapped to the `os` table.
    Disk: ORM class mapped to the `disk` table.
    VirtualInterface: ORM class mapped to the `virtual_interface` table.
    ProtocolGraphicInterface: ORM class mapped to the
        `protocol_graphic_interface` table.
    RAM: ORM class mapped to the `ram` table.

Functions:
    start_mappers: Configures the ORM mappings for all defined classes.
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

# Metadata instance used for SQLAlchemy table definitions
metadata = MetaData()

# Registry for managing class-to-table mappings
mapper_registry = registry(metadata=metadata)

# Table definitions
virtual_machines = Table(
    'virtual_machines',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('power_state', String(30)),
    Column('status', String(30)),
    Column('name', String(60)),
    Column('description', String(255)),
    Column('information', Text),
    Column('user_id', postgresql.UUID(as_uuid=True)),
)

cpu_info = Table(
    'cpu_info',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('cores', Integer, nullable=True),
    Column('threads', Integer, nullable=True),
    Column('sockets', Integer, nullable=True),
    Column('type', String(30)),
    Column('model', String(30)),
    Column(
        'vm_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_machines.id'),
    ),
    Column('vcpu', Integer, nullable=True),
)

os = Table(
    'os',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('os_type', String(80)),
    Column('os_variant', String(255)),
    Column('boot_device', String(10)),
    Column('graphic_driver', String(30)),
    Column('bios', String(30)),
    Column(
        'vm_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_machines.id'),
    ),
)

disk = Table(
    'disk',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255)),
    Column('emulation', String(30)),
    Column('format', String(20)),
    Column('qos', postgresql.JSON()),
    Column('boot_order', Integer),
    Column('path', String(255)),
    Column('size', BigInteger),
    Column('provisioning', String(30)),
    Column('type', Integer),
    Column('order', Integer),
    Column(
        'vm_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_machines.id'),
    ),
    Column('disk_id', postgresql.UUID(as_uuid=True)),
    Column('read_only', Boolean(), default=False),
)

virtual_interface = Table(
    'virtual_interface',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('interface', String(60)),
    Column('mac', String(20)),
    Column('mode', String(30)),
    Column('portgroup', String(30)),
    Column('model', String(30)),
    Column('order', Integer),
    Column(
        'vm_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_machines.id'),
    ),
)

protocol_graphic_interface = Table(
    'protocol_graphic_interface',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('login', String(90)),
    Column('password', String(255)),
    Column('connect_type', String(30)),
    Column('url', String(255)),
    Column(
        'vm_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_machines.id'),
    ),
)

ram = Table(
    'ram',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('size', BigInteger),
    Column(
        'vm_id',
        postgresql.UUID(as_uuid=True),
        ForeignKey('virtual_machines.id'),
    ),
)


# ORM class definitions
class VirtualMachines:
    """ORM class mapped to the `virtual_machines` table."""

    pass


class CpuInfo:
    """ORM class mapped to the `cpu_info` table."""

    pass


class Os:
    """ORM class mapped to the `os` table."""

    pass


class Disk:
    """ORM class mapped to the `disk` table."""

    pass


class VirtualInterface:
    """ORM class mapped to the `virtual_interface` table."""

    pass


class ProtocolGraphicInterface:
    """ORM class mapped to the `protocol_graphic_interface` table."""

    pass


class RAM:
    """ORM class mapped to the `ram` table."""

    pass


# Function to configure mappings
def start_mappers() -> None:
    """Configures the ORM mappings for all defined classes.

    This function maps the ORM classes to their corresponding tables and
    sets up relationships between entities.

    Raises:
        SQLAlchemyError: If the mapper configuration fails.
    """
    mapper_registry.map_imperatively(
        VirtualMachines,
        virtual_machines,
        properties={
            'cpu': relationship(
                CpuInfo,
                backref='virtual_machine',
                uselist=False,
                cascade='all, delete-orphan',
            ),
            'os': relationship(
                Os,
                backref='virtual_machine',
                uselist=False,
                cascade='all, delete-orphan',
            ),
            'disks': relationship(
                Disk,
                backref='virtual_machine',
                order_by=disk.c.order,
                uselist=True,
                cascade='all, delete-orphan',
            ),
            'virtual_interfaces': relationship(
                VirtualInterface,
                backref='virtual_machine',
                order_by=virtual_interface.c.order,
                uselist=True,
                cascade='all, delete-orphan',
            ),
            'graphic_interface': relationship(
                ProtocolGraphicInterface,
                backref='virtual_machine',
                uselist=False,
                cascade='all, delete-orphan',
            ),
            'ram': relationship(
                RAM,
                backref='virtual_machine',
                uselist=False,
                cascade='all, delete-orphan',
            ),
        },
    )
    mapper_registry.map_imperatively(CpuInfo, cpu_info)
    mapper_registry.map_imperatively(Os, os)
    mapper_registry.map_imperatively(Disk, disk)
    mapper_registry.map_imperatively(VirtualInterface, virtual_interface)
    mapper_registry.map_imperatively(
        ProtocolGraphicInterface, protocol_graphic_interface
    )
    mapper_registry.map_imperatively(RAM, ram)
