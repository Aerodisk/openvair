"""Module for ORM mappings related to virtual machines.

This module defines the ORM mappings for various entities associated with
virtual machines, including CPU information, operating system details, disks,
virtual interfaces, protocol graphic interfaces, RAM and snapshots. It uses
SQLAlchemy to define table schemas and relationships between these entities.

Tables:
    virtual_machines: Table containing virtual machine details.
    cpu_info: Table containing CPU information for virtual machines.
    os: Table containing operating system details for virtual machines.
    disk: Table containing disk information for virtual machines.
    virtual_interface: Table containing network interface information.
    protocol_graphic_interface: Table containing graphic interface protocol
        details.
    ram: Table containing RAM information for virtual machines.
    snapshots: Table containing information about snapshots of virtual machine.

Classes:
    VirtualMachines: ORM class mapped to the `virtual_machines` table.
    CpuInfo: ORM class mapped to the `cpu_info` table.
    Os: ORM class mapped to the `os` table.
    Disk: ORM class mapped to the `disk` table.
    VirtualInterface: ORM class mapped to the `virtual_interface` table.
    ProtocolGraphicInterface: ORM class mapped to the
        `protocol_graphic_interface` table.
    RAM: ORM class mapped to the `ram` table.
    Snapshots: ORM class mapped to the `snapshots` table.

Functions:
    start_mappers: Configures the ORM mappings for all defined classes.
"""

import uuid
import datetime
from typing import List

from sqlalchemy import (
    JSON,
    UUID,
    Text,
    String,
    Boolean,
    Integer,
    DateTime,
    MetaData,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column
from sqlalchemy.dialects import postgresql

# Metadata instance used for SQLAlchemy table definitions
metadata = MetaData()


# Registry for managing class-to-table mappings
class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


# ORM class definitions
class VirtualMachines(Base):
    """ORM class mapped to the `virtual_machines` table."""

    __tablename__ = 'virtual_machines'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    power_state: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    information: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )

    cpu: Mapped['CpuInfo'] = relationship(
        'CpuInfo',
        back_populates='virtual_machine',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    os: Mapped['Os'] = relationship(
        'Os',
        back_populates='virtual_machine',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    disks: Mapped[List['Disk']] = relationship(
        'Disk',
        back_populates='virtual_machine',
        order_by='Disk.order',
        uselist=True,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    virtual_interfaces: Mapped[List['VirtualInterface']] = relationship(
        'VirtualInterface',
        back_populates='virtual_machine',
        order_by='VirtualInterface.order',
        uselist=True,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    graphic_interface: Mapped['ProtocolGraphicInterface'] = relationship(
        'ProtocolGraphicInterface',
        back_populates='virtual_machine',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    ram: Mapped['RAM'] = relationship(
        'RAM',
        back_populates='virtual_machine',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    snapshots: Mapped[List['Snapshots']] = relationship(
        'Snapshots',
        back_populates='virtual_machine',
        order_by='Snapshots.created_at',
        cascade='all, delete-orphan',
    )


class CpuInfo(Base):
    """ORM class mapped to the `cpu_info` table."""

    __tablename__ = 'cpu_info'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    cores: Mapped[int] = mapped_column(Integer, nullable=True)
    threads: Mapped[int] = mapped_column(Integer, nullable=True)
    sockets: Mapped[int] = mapped_column(Integer, nullable=True)
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    model: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=True,
    )
    vcpu: Mapped[int] = mapped_column(Integer, nullable=True)

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='cpu',
    )


class Os(Base):
    """ORM class mapped to the `os` table."""

    __tablename__ = 'os'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    os_type: Mapped[str] = mapped_column(
        String(80),
        nullable=True,
    )
    os_variant: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    boot_device: Mapped[str] = mapped_column(
        String(10),
        nullable=True,
    )
    graphic_driver: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    bios: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=True,
    )

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='os',
    )


class Disk(Base):
    """ORM class mapped to the `disk` table."""

    __tablename__ = 'disk'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    emulation: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    format: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    qos: Mapped[JSON] = mapped_column(
        postgresql.JSON(),
        nullable=True,
    )
    boot_order: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    path: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
    )
    provisioning: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=True,
    )
    disk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        nullable=True,
    )
    read_only: Mapped[bool] = mapped_column(
        Boolean(),
        default=False,
        nullable=True,
    )

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='disks',
    )


class VirtualInterface(Base):
    """ORM class mapped to the `virtual_interface` table."""

    __tablename__ = 'virtual_interface'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    interface: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    mac: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    mode: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    portgroup: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    model: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=True,
    )

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='virtual_interfaces',
    )


class ProtocolGraphicInterface(Base):
    """ORM class mapped to the `protocol_graphic_interface` table."""

    __tablename__ = 'protocol_graphic_interface'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(
        String(90),
        nullable=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    connect_type: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    url: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=True,
    )

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='graphic_interface',
    )


class RAM(Base):
    """ORM class mapped to the `ram` table."""

    __tablename__ = 'ram'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=True,
    )

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='ram',
    )


class Snapshots(Base):
    """ORM class mapped to the `snapshots` table."""

    __tablename__ = 'snapshots'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    vm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('virtual_machines.id'),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey('snapshots.id'),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now,
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    virtual_machine: Mapped[VirtualMachines] = relationship(
        'VirtualMachines',
        back_populates='snapshots',
        lazy='selectin',
    )
    parent: Mapped['Snapshots'] = relationship(
        'Snapshots',
        foreign_keys=[parent_id],
        remote_side=[id],
        lazy='selectin',
    )
