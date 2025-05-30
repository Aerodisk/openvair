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
from typing import List, Union, Literal, Optional

from pydantic import BaseModel


class Cpu(BaseModel):
    """Schema for CPU information."""

    cores: Optional[int] = 1
    threads: Optional[int] = 1
    sockets: Optional[int] = 1
    model: Literal['host'] = 'host'
    type: Literal['static', 'dynamic'] = 'static'
    vcpu: Optional[int] = None


class RAM(BaseModel):
    """Schema for RAM information."""

    size: int


class Os(BaseModel):
    """Schema for operating system information."""

    os_type: Optional[str] = 'Linux'  # Linux or others unix types
    os_variant: Optional[str] = 'Ubuntu 20.04'  # Ubuntu or others unix os
    boot_device: Literal['hd', 'cdrom'] = 'cdrom'
    bios: Literal['LEGACY', 'UEFI', 'ACCORD'] = 'LEGACY'
    graphic_driver: Literal['virtio', 'vga'] = 'virtio'


class GraphicInterfaceBase(BaseModel):
    """Base schema for graphic interface information."""

    login: Optional[str] = None
    password: Optional[str] = None
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
    portgroup: Optional[str] = None
    interface: str
    mac: str = '6C:4A:74:B4:FD:59'  # default start 6C:4A:74:
    model: Literal['virtio'] = 'virtio'
    order: Optional[int] = None


class QOS(BaseModel):
    """Schema for Quality of Service settings for disks."""

    iops_read: int = 500
    iops_write: int = 500
    mb_read: int = 150
    mb_write: int = 150


class Disk(BaseModel):
    """Schema for disk information."""

    name: Optional[str] = None
    emulation: Literal['virtio', 'ide', 'scsi'] = 'virtio'
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

    attach_disks: List[
        Optional[Union[AttachVolume, AttachImage, AutoCreateVolume]]
    ]


class CreateVirtualMachine(BaseModel):
    """Schema for creating a virtual machine."""

    name: str  # VM name
    description: Optional[str] = None
    os: Os
    cpu: Cpu
    ram: RAM
    graphic_interface: GraphicInterfaceBase
    disks: CreateVmDisks
    virtual_interfaces: List[VirtualInterface]


class DiskInfo(BaseModel):
    """Schema for detailed disk information."""

    id: int
    name: Optional[str] = None
    emulation: Optional[str] = None  # virtio
    format: Optional[str] = None  # qcow2 or raw
    qos: Optional[QOS] = None
    boot_order: Optional[int] = None
    order: Optional[int] = None
    path: Optional[str] = None
    size: Optional[int] = None
    provisioning: Optional[str] = None
    disk_id: Optional[str] = None
    type: Optional[int] = None
    read_only: bool = False


class VirtualInterfaceInfo(VirtualInterface):
    """Schema for detailed virtual network interface information."""

    id: int


class GraphicInterfaceInfo(GraphicInterfaceBase):
    """Schema for detailed graphic interface information."""

    url: Optional[str] = None


class VirtualMachineInfo(BaseModel):
    """Schema for detailed virtual machine information."""

    id: str
    name: str
    power_state: str
    status: str
    description: Optional[str] = None
    information: Optional[str] = None
    cpu: Cpu
    ram: RAM
    os: Os
    graphic_interface: GraphicInterfaceInfo
    disks: List[Optional[DiskInfo]]
    virtual_interfaces: List[VirtualInterfaceInfo]


class ListOfVirtualMachines(BaseModel):
    """Schema for a list of virtual machines."""

    virtual_machines: List[Optional[VirtualMachineInfo]]


class DetachDisk(BaseModel):
    """Schema for detaching a disk."""

    id: int


class EditDisk(Disk):
    """Schema for editing disk information."""

    id: int


class EditVmDisks(BaseModel):
    """Schema for editing virtual machine disks."""

    attach_disks: List[
        Optional[Union[AttachVolume, AttachImage, AutoCreateVolume]]
    ]
    detach_disks: List[Optional[DetachDisk]]
    edit_disks: List[Optional[EditDisk]]


class DetachVirtualInterface(BaseModel):
    """Schema for detaching a virtual network interface."""

    id: int


class EditVirtualInterface(VirtualInterface):
    """Schema for editing a virtual network interface."""

    id: int


class EditVirtualInterfaces(BaseModel):
    """Schema for editing virtual machine interfaces."""

    new_virtual_interfaces: List[Optional[VirtualInterface]]
    detach_virtual_interfaces: List[Optional[DetachVirtualInterface]]
    edit_virtual_interfaces: List[Optional[EditVirtualInterface]]


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


class Vnc(BaseModel):
    """Schema for VNC session details."""

    url: str = ''  # http://matrix:6900/vnc.html?host=matrix&port=6900


class SnapshotInfo(BaseModel):
    """Schema for detailed snapshot information.

    Attributes:
        vm_id (UUID): The ID of the virtual machine.
        id (UUID): The ID of the snapshot.
        name (str): The name of the snapshot.
        parent (Optional[str]): The optional name of the parent snapshot.
        description (Optional[str]): The optional description of the snapshot.
    """
    # TODO: Решить, использовать name (str) или ID (UUID) для parent
    vm_id: UUID
    id: UUID
    name: str
    parent: Optional[str] = None
    description: Optional[str] = None


class ListOfSnapshots(BaseModel):
    """Schema for a list of snapshots of specific virtual machine.

    Attributes:
        snapshots(List[Optional[SnapshotInfo]]): The list of snapshots.
    """

    snapshots: List[Optional[SnapshotInfo]]


class CreateSnapshot(BaseModel):
    """Schema for creating a snapshot of the virtual machine.

    Attributes:
        name (str): The name of the new snapshot.
        description (Optional[str]): The optional description of the snapshot.
    """

    name: str
    description: Optional[str] = None


# class RevertSnapshot(BaseModel):
#     """Schema for reverting virtual machine to the snapshot.
#
#     Attributes:
#         id (UUID): The ID of the snapshot to revert.
#     """
#
#     id: UUID
#
#
# class DeleteSnapshot(BaseModel):
#     """Schema for deleting snapshot of the virtual machine.
#
#     Attributes:
#         id (UUID): The ID of snapshot to delete.
#     """
#
#     id: UUID
