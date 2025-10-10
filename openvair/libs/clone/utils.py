"""Clone utilities.

Functions:
    get_max_clone_number: finds the highest clone suffix number in names
        like `<base_name>_clone_<NN>`. It also ensures creating `count` new
        clones won't exceed the max suffix (99). Raises
        `NoAvailableNameForClone` if no suffix is available.
"""

import re
import secrets
from typing import Set, List, Optional

from openvair.libs.log import get_logger
from openvair.libs.clone.exceptions import (
    CloneNameTooLong,
    NoAvailableMacForClone,
    NoAvailableNameForClone,
)

LOG = get_logger(__name__)


def get_max_clone_number(
    base_name: str, existing_names: List[str], count: int
) -> int:
    """Gets max clone suffix number matching '<base_name>_clone_<NNN>'.

    Checks that creating new clones won't exceed the maximum suffix of 99.
    Raises an exception if there are no available names.

    Args:
        base_name (str): The base name of the object to clone.
        existing_names (list[str]): List of existing object names.
        count (int): Number of clones to create.

    Raises:
        NoAvailableNameForClone: If there is no available suffix.

    Returns:
        int: The highest existing clone suffix number.
    """
    pattern = re.compile(rf'^{re.escape(base_name)}_clone_(\d+)$')
    max_num = 0
    for name in existing_names:
        match = pattern.match(name)
        num = int(match.group(1)) if match else 0
        max_num = num if num > max_num else max_num
    max_suff = 999
    if max_num >= max_suff or max_num + count > max_suff:
        msg = 'No available name for clone'
        LOG.error(msg)
        raise NoAvailableNameForClone(msg)
    return max_num


def create_new_clone_name(
    name: str, num: int, max_len: Optional[int] = None
) -> str:
    """Creates a name of a clone.

    Raises:
        CloneNameTooLong: If the clone name will exceed the maximum length
    """
    suff_len = 10  # length of the suffix "_clone_<NNN>"
    if max_len and len(name) + suff_len > max_len:
        msg = f'VM or disk name is too long: len {name} > {max_len - suff_len}'
        LOG.error(msg)
        raise CloneNameTooLong(msg)

    return f'{name}_clone_{num:03d}'


def generate_mac_address() -> str:
    """Generates a random MAC address.

    Returns:
        str: Random MAC address (default format: '6C:4A:74:XX:XX:XX')
    """
    prefix = "6C:4A:74"  # default
    random_part = ":".join(
        "".join(secrets.choice("0123456789ABCDEF") for _ in range(2))
        for _ in range(3)
    )
    return f"{prefix}:{random_part}"


def generate_unique_macs(
        existing_macs: Set[str],
        count: int,
        max_attempts: int = 100
) -> List[str]:
    """Generates multiple unique MAC addresses.

    Args:
        existing_macs (Set[str]): Set of existing MAC addresses to avoid.
        count (int): Number of unique MAC addresses to generate.
        max_attempts (int): Maximum attempts to generate unique MAC.

    Raises:
        NoAvailableMacForClone: If can't generate unique MAC after max_attempts.

    Returns:
        List[str]: List of generated unique MAC addresses.
    """
    generated_macs = set()

    for _ in range(count):
        for __ in range(max_attempts):
            mac = generate_mac_address()
            if mac not in existing_macs and mac not in generated_macs:
                generated_macs.add(mac)
                break
        else:
            msg = (f'Cannot generate unique MAC '
                   f'address after {max_attempts} attempts')
            LOG.error(msg)
            raise NoAvailableMacForClone(msg)

    return list(generated_macs)
