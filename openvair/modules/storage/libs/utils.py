"""Block device utilities.

This module provides helper functions to retrieve and analyze block device
information from the system using the 'lsblk' command and parse the results.

Functions:
- get_block_devices_info: Retrieves details for all block devices.
- get_system_disks: Retrieves details for local disks (optionally with
    children).
- is_system_disk: Checks if a given disk is a system disk.
- get_local_partitions: Retrieves details for local partitions.
- is_system_partition: Checks if a given partition is a system partition.
"""

from typing import (
    Any,
    Dict,
    List,
)

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.data_handlers.json.serializer import deserialize_json

LOG = get_logger(__name__)

SYSTEM_MOUNTPOINTS = [
    '/',
    '/bin',
    '/boot',
    '/dev',
    '/etc',
    '/etc/X11',
    '/etc/apt',
    '/etc/samba',
    '/home',
    '/lib',
    '/media',
    '/opt',
    '/proc',
    '/root',
    '/sbin',
    '/srv',
    '/tmp',  # noqa: S108 because it's a system directory
    '/usr',
    '/usr/bin',
    '/usr/include',
    '/usr/lib',
    '/usr/sbin',
    '/usr/share',
    '/usr/src',
    '/usr/local',
    '/var',
    '/var/cache',
    '/var/lib',
    '/var/lock',
    '/var/log',
    '/var/mail',
    '/var/run',
    '/var/spool',
    '/var/tmp',  # noqa: S108 because it's a system directory
    '/var/www',
]


def get_block_devices_info() -> List[Dict[str, Any]]:
    """Retrieve information about block devices on the system.

    Uses the 'lsblk' command (with JSON output) to gather details about block
    devices. If the command fails or returns invalid data, an empty list is
    returned.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information
            about each block device. The keys typically include:
            'name', 'size', 'type', 'mountpoint', 'uuid', 'fstype', and
            optionally 'children'.
    """
    res = execute(
        'lsblk',
        '-bp',
        '-io',
        'NAME,SIZE,TYPE,MOUNTPOINT,UUID,FSTYPE',
        '--json',
        params=ExecuteParams(shell=True),  # noqa: S604
    )
    result: List[Dict[str, str]] = deserialize_json(res.stdout)['blockdevices']
    return result



def get_system_disks(*, is_need_children: bool = False) -> List[Dict[str, Any]]:
    """Retrieve information about local disks on the system.

    Uses `get_block_devices_info` to gather details about local disks
    (type='disk'), optionally including child partitions.

    Args:
        is_need_children (bool): Whether to include child devices in the result.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with information about
            local disks. Each dictionary typically has the keys:
            - 'path'
            - 'size'
            - 'mountpoint'
            - 'fs_uuid'
            - 'type'
            - 'fstype'
            - 'children' (optional, if is_need_children=True)
    """
    block_devices: List[Dict[str, Any]] = get_block_devices_info()

    disks = []
    for block_device in block_devices:
        if block_device.get('type') == 'disk':
            disk_info = {
                'path': block_device.get('name'),
                'size': int(block_device.get('size', 0)),
                'mountpoint': block_device.get('mountpoint'),
                'fs_uuid': block_device.get('uuid'),
                'type': block_device.get('type'),
                'fstype': block_device.get('fstype'),
            }

            if is_need_children:
                disk_info.update({'children': block_device.get('children', [])})
            disks.append(disk_info)

    return disks


def is_system_disk(path: str) -> bool:
    """Check if a given disk path corresponds to a system disk.

    A disk is considered a system disk if one of its child partitions
    is mounted at '/'.

    Args:
        path (str): The path of the disk to check, e.g. '/dev/sda'.

    Returns:
        bool: True if the disk is a system disk, False otherwise.
    """
    disks = {
        disk_info.get('path'): disk_info
        for disk_info in get_system_disks(is_need_children=True)
    }
    checked_disk = disks.get(path, {})
    for child in checked_disk.get('children', []):
        if child.get('mountpoint') == '/':
            return True
    return False


def get_local_partitions() -> List[Dict[str, Any]]:
    """Retrieve information about local partitions on the system.

    Uses `get_system_disks` with `is_need_children=True` to gather details
    about partitions. Each partition is annotated with its parent disk path
    before returning.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with information about
            local partitions. Each dictionary typically has keys:
            - 'name'
            - 'parent'
            - 'path'
            - 'mountpoint'
            - 'fs_uuid'
            - 'fstype'
    """
    block_devices = get_system_disks(is_need_children=True)

    partitions = []
    for block_device in block_devices:
        children = []
        for child in block_device.get('children', []):
            child['parent'] = block_device.get('path')
            child['path'] = child.get('name')
            child['mountpoint'] = child.get('mountpoint')
            child['fs_uuid'] = child.get('uuid')
            children.append(child)
        partitions += children

    return partitions


def is_system_partition(disk_path: str, part_num: str) -> bool:
    """Check if a partition is a system partition.

    A partition is considered a system partition if its mount point is listed in
    SYSTEM_MOUNTPOINTS (e.g., '/', '/boot', etc.).

    Args:
        disk_path (str): The path of the disk containing the partition, e.g. '/dev/sda'.
        part_num (str): The partition number (suffix), e.g. '1' if partition path is '/dev/sda1'.

    Returns:
        bool: True if the partition is a system partition, False otherwise.
    """  # noqa: E501, W505
    block_devices = get_system_disks(is_need_children=True)

    disk: Dict = next(
        filter(lambda device: device.get('path') == disk_path, block_devices)
    )

    partition_path = f'{disk_path}{part_num}'
    partition: Dict = next(
        filter(
            lambda part: part.get('name') == partition_path,
            disk['children'],
        )
    )

    return partition.get('mountpoint') in SYSTEM_MOUNTPOINTS
