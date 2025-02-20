"""Utility functions and classes for OpenVair.

This module provides various utility functions and classes used across the
OpenVair application, including command execution, token generation, validation,
and disk information retrieval.

Functions:
    create_access_token: Creates a JWT access token.
    create_refresh_token: Creates a JWT refresh token.
    create_tokens: Generates both access and refresh tokens.
    get_current_user: Retrieves the user from a JWT token.
    get_block_devices_info: Retrieves information about block devices.
    get_system_disks: Retrieves information about local disks.
    is_system_disk: Checks if a disk is a system disk.
    get_local_partitions: Retrieves information about local partitions.
    is_system_partition: Checks if a partition is a system partition.
    lip_scan: Performs LIP (Loop Initialization Protocol) scan.
    get_size: Returns the size of a file.
    validate_objects: Validates a list of objects against a Pydantic schema.
    write_yaml_file: Writes data to a YAML file.
    read_yaml_file: Reads data from a YAML file.
    synchronized_session: Context manager for safely executing database
        session operations.
"""

import os
import json
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Union,
    Optional,
    Generator,
)
from pathlib import Path
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager

import jwt
import yaml
import xmltodict
from fastapi import Depends, HTTPException, security
from sqlalchemy.exc import OperationalError

from openvair import config
from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

LOG = get_logger(__name__)

# JWT configuration settings
JWT_SECRET = config.data['jwt'].get('secret')
TOKEN_TYPE = config.data['jwt'].get('token_type')
ALGORITHM = config.data['jwt'].get('algorithm')
ACCESS_TOKEN_EXPIRE_MINUTES = config.data['jwt'].get(
    'access_token_expiration_minutes', 30
)
REFRESH_TOKEN_EXPIRATION_DAYS = config.data['jwt'].get(
    'refresh_token_expiration_days', 7
)

oauth2schema = security.OAuth2PasswordBearer('/auth/')

# List of system mount points
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
    '/tmp',  # noqa: S108 because its system directory
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
    '/var/tmp',  # noqa: S108 because its system directory
    '/var/www',
]


def create_access_token(user: Dict, ttl_minutes: Optional[int] = None) -> str:
    """Creates a JWT access token.

    Args:
        user (Dict): The user object to encode in the token.
        ttl_minutes (Optional[int]): The time-to-live (TTL) for the token in
            minutes.

    Returns:
        str: The encoded access token.

    Raises:
        HTTPException: If token creation fails.
    """
    try:
        payload = user.copy()
        LOG.info(f'Start creating access token with payload: {payload}')

        # Use timedelta to add the TTL to the current time
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ttl_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload.update({'exp': expire, 'type': 'access'})

        token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=ALGORITHM)
        LOG.info(f'Created access token data: {token}')

    except jwt.PyJWTError as error:
        LOG.error(f'Access token creation failed: {error}')
        raise HTTPException(
            status_code=400, detail='Invalid username or password'
        )
    else:
        return token


def create_refresh_token(user: Dict, ttl_days: Optional[int] = None) -> str:
    """Creates a JWT refresh token.

    Args:
        user (Dict): The user object to encode in the token.
        ttl_days (Optional[int]): The time-to-live (TTL) for the refresh token
            in days.

    Returns:
        str: The encoded refresh token.

    Raises:
        HTTPException: If token creation fails.
    """
    try:
        payload = user.copy()
        LOG.info(f'Start creating refresh token with payload: {payload}')

        # Use timedelta to add the TTL to the current time
        expire = datetime.now(timezone.utc) + timedelta(
            days=ttl_days or REFRESH_TOKEN_EXPIRATION_DAYS
        )

        payload.update({'exp': expire, 'type': 'refresh'})

        token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=ALGORITHM)
        LOG.info(f'Created refresh token data: {token}')
    except jwt.PyJWTError as error:
        LOG.error(f'Refresh token creation failed: {error}')
        raise HTTPException(
            status_code=400, detail='Invalid username or password'
        )
    else:
        return token


def create_tokens(user: Dict) -> Dict:
    """Creates a dictionary containing access and refresh tokens.

    Args:
        user (Dict): The user object to encode in the tokens.

    Returns:
        Dict: A dictionary containing the access and refresh tokens.
    """
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': TOKEN_TYPE,
    }


def get_current_user(token: str = Depends(oauth2schema)) -> Dict:
    """Retrieves the current user from a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Dict: The user object decoded from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload: Dict = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[
                ALGORITHM,
            ],
        )

        if payload['type'] != 'access':
            raise HTTPException(status_code=401, detail='Invalid access token')

        payload.update({'token': token})
        LOG.info(f'User authenticated: {payload["username"]}')
    except jwt.ExpiredSignatureError:
        LOG.error('Token expired')
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        LOG.error('Invalid token')
        raise HTTPException(status_code=401, detail='Invalid token')
    else:
        return payload


def get_block_devices_info() -> List[Dict[str, str]]:
    """Retrieves information about block devices on the system.

    Uses the 'lsblk' command to gather details about block devices.

    Returns:
        List[Dict[str, str]]: A dictionary containing information about block
            devices.
    """
    res = execute(
        'lsblk',
        '-bp',
        '-io',
        'NAME,SIZE,TYPE,MOUNTPOINT,UUID,FSTYPE',
        '--json',
        params=ExecuteParams(  # noqa: S604
            shell=True,
        ),
    )
    result: List[Dict[str, str]] = json.loads(res.stdout)['blockdevices']
    return result


def get_system_disks(*, is_need_children: bool = False) -> List[Dict]:
    """Retrieves information about local disks on the system.

    Uses the 'lsblk' command to gather details about local disks, optionally
    including information about child devices.

    Args:
        is_need_children (bool): Whether to include child devices in the output.

    Returns:
        List[Dict]: A list containing dictonaties with information about local
            disks.
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
    """Checks if a given disk path corresponds to a system disk.

    Args:
        path (str): The path of the disk to check.

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


def get_local_partitions() -> List[Dict]:
    """Retrieves information about local partitions on the system.

    Uses the 'lsblk' command to gather details about local partitions.

    Returns:
        List[Dict]: A list containing dictonaries with information about local
            partitions.
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
    """Checks if a partition is a system partition.

    Args:
        disk_path (str): The path of the disk containing the partition.
        part_num (str): The partition number to check.

    Returns:
        bool: True if the partition is a system partition, False otherwise.
    """
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


def lip_scan() -> None:
    """Performs Loop Initialization Protocol scan om Fibre Channel host adapters

    This function initiates a LIP scan by writing '1' to the 'issue_lip' file
    for all Fibre Channel host adapters.

    Raises:
        OSError: If there is an error accessing or writing to the 'issue_lip'
            file.
    """
    try:
        # Execute the command to issue LIP scan for all Fibre Channel
        # host adapters
        execute(
            'for i in /sys/class/fc_host/*; do sudo sh -c "echo 1 > $i/issue_lip"; done',  # noqa: E501 because need one line command for better readability
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
                raise_on_error=True,
            ),
        )
    except (ExecuteError, OSError) as e:
        # Handle any errors accessing or writing to the file
        msg = (
            f'Error accessing or writing to /sys/class/fc_host/*/issue_lip: {e}'
        )
        LOG.error(msg)
        raise


def get_size(file_path: str) -> int:
    """Returns the size of the specified file.

    Args:
        file_path (str): The path of the file to check.

    Returns:
        int: The size of the file in bytes.
    """
    return Path(file_path).stat().st_size


def write_yaml_file(file_path: str, data: Dict) -> None:
    """Writes data to a YAML file.

    Args:
        file_path (str): The path of the YAML file to write to.
        data (Dict): The data to write to the file.
    """
    with Path(file_path).open('w') as file:
        yaml.dump(data, file, sort_keys=False)


def read_yaml_file(file_path: str) -> Dict:
    """Reads data from a YAML file.

    Args:
        file_path (str): The path of the YAML file to read from.

    Returns:
        Dict: The data read from the YAML file.
    """
    with Path(file_path).open('r') as file:
        result: Dict = yaml.safe_load(file)
        return result


@contextmanager
def synchronized_session(session: 'Session') -> Generator:
    """Creates a context for safely executing database session operations.

    This decorator creates a nested transaction within the current transaction
    of the session. It ensures that changes are committed or rolled back in case
    of an error.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy session to execute
            operations on.

    Yields:
        sqlalchemy.orm.Session: The SQLAlchemy session within the
            synchronization context.

    Raises:
        Exception: Any exception raised within the synchronization context will
            be caught and re-raised.
    """
    try:
        yield session.begin_nested()
        session.commit()
    except OperationalError:
        session.rollback()


def xml_to_jsonable(xml_string: str) -> Union[Dict, List]:
    """Getting xml file and conver it to List or Dict"""

    def remove_prefix(d: Union[Dict, List]) -> Union[Dict, List]:
        """Remove '@' prefix for keys for parsed data"""
        if isinstance(d, Dict):
            new_dict = {}
            for k, v in d.items():
                # Убираем префикс, если он есть
                new_key = k.lstrip('@') if k.startswith('@') else k
                new_dict[new_key] = remove_prefix(v)
            return new_dict

        if isinstance(d, List):
            return [remove_prefix(i) for i in d]

        return d

    # Парсим XML и убираем префиксы
    parsed_dict = xmltodict.parse(xml_string)
    return remove_prefix(parsed_dict)


@contextmanager
def change_directory(
    destination: Path,
) -> Generator[None, Any, None]:
    """Context manager to temporarily change the working directory.

    This context manager changes the current working directory to the specified
    destination for the duration of the context. After exiting the context, it
    restores the original working directory.

    Args:
        destination (Path): The directory to change to during the context.

    Yields:
        None: No values are yielded; the context simply changes the directory.

    Example:
        with change_directory("/tmp"):
            # Current working directory is now "/tmp".
            ...

        # Original working directory is restored.
    """
    original_directory = Path.cwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(original_directory)
