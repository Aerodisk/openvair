"""Module for API schemas related to virtual machines.

This module defines the data schemas used for validation and serialization
of virtual machine-related data in the API. It uses Pydantic models to
define the structure of the data.

Classes:
    Cpu: Schema for CPU information.
    RAM: Schema for RAM information.
    Os: Schema for operating system information.
    GraphicInterfaceBase: Base schema for graphic interface information.
    VirtualInterface: Schema for virtual network interface information.
    QOS: Schema for Quality of Service settings for disks.
    Disk: Schema for disk information.
    AttachVolume: Schema for attaching an existing volume as a disk.
    AutoCreateVolume: Schema for automatically creating and attaching a
        new volume as a disk.
    AttachImage: Schema for attaching an image as a disk.
    CreateVmDisks: Schema for creating virtual machine disks.
    CreateVirtualMachine: Schema for creating a virtual machine.
    DiskInfo: Schema for detailed disk information.
    VirtualInterfaceInfo: Schema for detailed virtual network interface
        information.
    GraphicInterfaceInfo: Schema for detailed graphic interface
        information.
    VirtualMachineInfo: Schema for detailed virtual machine information.
    ListOfVirtualMachines: Schema for a list of virtual machines.
    DetachDisk: Schema for detaching a disk.
    EditDisk: Schema for editing disk information.
    EditVmDisks: Schema for editing virtual machine disks.
    DetachVirtualInterface: Schema for detaching a virtual network
        interface.
    EditVirtualInterface: Schema for editing a virtual network interface.
    EditVirtualInterfaces: Schema for editing virtual machine interfaces.
    EditVm: Schema for editing a virtual machine.
    Vnc: Schema for VNC session details.
    SnapshotInfo: Schema for detailed snapshot information.
    ListOfSnapshots: Schema for a list of snapshots of specific virtual machine.
    CreateSnapshot: Schema for creating a snapshot of virtual machine.
"""

from uuid import UUID
from typing import Literal

from pydantic import Field, BaseModel


class Cpu(BaseModel):
    """Schema for CPU information."""

    cores: int | None = 1
    threads: int | None = 1
    sockets: int | None = 1
    model: Literal['host'] = 'host'
    type: Literal['static', 'dynamic'] = 'static'
    vcpu: int | None = None


class RAM(BaseModel):
    """Schema for RAM information."""

    size: int


class Os(BaseModel):
    """Schema for operating system information."""

    os_type: str | None = 'Linux'  # Linux or others unix types
    os_variant: str | None = 'Ubuntu 20.04'  # Ubuntu or others unix os
    boot_device: Literal['hd', 'cdrom'] = 'cdrom'
    bios: Literal['LEGACY', 'UEFI', 'ACCORD'] = 'LEGACY'
    graphic_driver: Literal['virtio', 'vga'] = 'virtio'


class GraphicInterfaceBase(BaseModel):
    """Base schema for graphic interface information."""

    login: str | None = None
    password: str | None = None
    connect_type: Literal['vnc', 'spice'] = 'vnc'


class VirtualInterface(BaseModel):
    """Schema for virtual network interface information."""

    mode: Literal[
        'bridge',
        'nat',
        'default',
        'isolated',
        'vepa',
        'user',
        'virtual_network',
    ] = 'bridge'  # default???????
    portgroup: str | None = None
    interface: str
    mac: str = '6C:4A:74:B4:FD:59'  # default start 6C:4A:74:
    model: Literal['virtio', 'bridge'] = 'virtio'
    order: int | None = None


class QOS(BaseModel):
    """Schema for Quality of Service settings for disks."""

    iops_read: int = 500
    iops_write: int = 500
    mb_read: int = 150
    mb_write: int = 150


class Disk(BaseModel):
    """Schema for disk information."""

    name: str | None = None
    emulation: Literal['virtio', 'ide', 'scsi', 'sata'] = 'virtio'
    format: Literal['qcow2', 'raw'] = 'qcow2'
    qos: QOS
    boot_order: int
    order: int
    read_only: bool = False


class AttachVolume(Disk):
    """Schema for attaching an existing volume as a disk."""

    volume_id: str


class AutoCreateVolume(Disk):
    """Schema for automatically creating and attaching a new volume as a disk"""

    storage_id: str
    size: int


class AttachImage(Disk):
    """Schema for attaching an image as a disk."""

    image_id: str


class CreateVmDisks(BaseModel):
    """Schema for creating virtual machine disks."""

    attach_disks: list[
        AttachVolume | AttachImage | AutoCreateVolume | None
    ]


class CreateVirtualMachine(BaseModel):
    """Schema for creating a virtual machine."""

    name: str  # VM name
    description: str | None = None
    os: Os
    cpu: Cpu
    ram: RAM
    graphic_interface: GraphicInterfaceBase
    disks: CreateVmDisks
    virtual_interfaces: list[VirtualInterface]


class DiskInfo(BaseModel):
    """Schema for detailed disk information."""

    id: int
    name: str | None = None
    emulation: str | None = None  # virtio
    format: str | None = None  # qcow2 or raw
    qos: QOS | None = None
    boot_order: int | None = None
    order: int | None = None
    path: str | None = None
    size: int | None = None
    provisioning: str | None = None
    disk_id: str | None = None
    type: str | None = None
    read_only: bool = False


class VirtualInterfaceInfo(VirtualInterface):
    """Schema for detailed virtual network interface information."""

    id: int


class GraphicInterfaceInfo(GraphicInterfaceBase):
    """Schema for detailed graphic interface information."""

    url: str | None = None


class VirtualMachineInfo(BaseModel):
    """Schema for detailed virtual machine information."""

    id: str
    name: str
    power_state: str
    status: str
    description: str | None = None
    information: str | None = None
    cpu: Cpu
    ram: RAM
    os: Os
    graphic_interface: GraphicInterfaceInfo
    disks: list[DiskInfo | None]
    virtual_interfaces: list[VirtualInterfaceInfo]


class ListOfVirtualMachines(BaseModel):
    """Schema for a list of virtual machines."""

    virtual_machines: list[VirtualMachineInfo | None]


class DetachDisk(BaseModel):
    """Schema for detaching a disk."""

    id: int


class EditDisk(Disk):
    """Schema for editing disk information."""

    id: int


class EditVmDisks(BaseModel):
    """Schema for editing virtual machine disks."""

    attach_disks: list[
        AttachVolume | AttachImage | AutoCreateVolume | None
    ]
    detach_disks: list[DetachDisk | None]
    edit_disks: list[EditDisk | None]


class DetachVirtualInterface(BaseModel):
    """Schema for detaching a virtual network interface."""

    id: int


class EditVirtualInterface(VirtualInterface):
    """Schema for editing a virtual network interface."""

    id: int


class EditVirtualInterfaces(BaseModel):
    """Schema for editing virtual machine interfaces."""

    new_virtual_interfaces: list[VirtualInterface | None]
    detach_virtual_interfaces: list[DetachVirtualInterface | None]
    edit_virtual_interfaces: list[EditVirtualInterface | None]


class EditVm(BaseModel):
    """Schema for editing a virtual machine."""

    name: str
    description: str
    cpu: Cpu
    ram: RAM
    os: Os
    graphic_interface: GraphicInterfaceBase
    disks: EditVmDisks
    virtual_interfaces: EditVirtualInterfaces


class CloneVm(BaseModel):
    """Schema for cloning a virtual machine."""

    count: int = Field(1, description='Number of clones')
    target_storage_id: UUID = Field(
        ..., description='ID of storage where the volume will be created'
    )


class Vnc(BaseModel):
    """Schema for VNC session details."""

    url: str = ''  # http://matrix:6900/vnc.html?host=matrix&port=6900


class SnapshotInfo(BaseModel):
    """Schema for detailed snapshot information.

    Attributes:
        vm_id (UUID): The ID of the virtual machine.
        id (UUID): The ID of the snapshot.
        vm_name (str): The name of the virtual machine.
        name (str): The name of the snapshot.
        parent (Optional[str]): The optional name of the parent snapshot.
        description (Optional[str]): The optional description of the snapshot.
        created_at (str): The creation time of the snapshot.
        is_current (bool): The flag of the current snapshot.
        status (str): The status of the snapshot.
    """

    vm_id: UUID
    id: UUID
    vm_name: str
    name: str
    parent: str | None = None
    description: str | None = None
    created_at: str
    is_current: bool
    status: str


class ListOfSnapshots(BaseModel):
    """Schema for a list of snapshots of specific virtual machine.

    Attributes:
        snapshots(List[Optional[SnapshotInfo]]): The list of snapshots.
    """

    snapshots: list[SnapshotInfo | None]


class CreateSnapshot(BaseModel):
    """Schema for creating a snapshot of the virtual machine.

    Attributes:
        name (str): The name of the new snapshot.
        description (Optional[str]): The optional description of the snapshot.
    """

    name: str
    description: str | None = None
