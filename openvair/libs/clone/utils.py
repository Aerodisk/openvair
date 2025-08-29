"""Clone utilities.

Functions:
    get_max_clone_number: finds the highest clone suffix number in names
        like `<base_name>_clone_<NN>`. It also ensures creating `count` new
        clones won't exceed the max suffix (99). Raises
        `NoAvailableNameForClone` if no suffix is available.
"""

import re
from typing import List, Optional

from openvair.libs.log import get_logger
from openvair.libs.clone.exceptions import (
    CloneNameTooLong,
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
