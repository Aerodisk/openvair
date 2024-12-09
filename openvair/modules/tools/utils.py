"""Utility functions and classes for OpenVair.

This module provides various utility functions and classes used across the
OpenVair application, including command execution, token generation, validation,
and disk information retrieval.

Functions:
    execute: Runs a shell command and returns the output.
    create_access_token: Creates a JWT access token.
    create_refresh_token: Creates a JWT refresh token.
    create_tokens: Generates both access and refresh tokens.
    get_current_user: Retrieves the user from a JWT token.
    is_superuser: Validates if the current user is a superuser.
    get_block_devices_info: Retrieves information about block devices.
    get_system_disks: Retrieves information about local disks.
    is_system_disk: Checks if a disk is a system disk.
    get_local_partitions: Retrieves information about local partitions.
    is_system_partition: Checks if a partition is a system partition.
    lip_scan: Performs LIP (Loop Initialization Protocol) scan.
    get_size: Returns the size of a file.
    validate_objects: Validates a list of objects against a Pydantic schema.
    get_virsh_list: Retrieves a list of virtual machines from virsh.
    regex_matcher: Returns regex patterns for various types of values.
    write_yaml_file: Writes data to a YAML file.
    read_yaml_file: Reads data from a YAML file.
    synchronized_session: Context manager for safely executing database
        session operations.

Classes:
    UnknownArgumentError: Raised when an unknown argument is passed to a
        function.
    NoRootWrapSpecifiedError: Raised when a command requests root but no
        root helper is specified.
    ExecuteTimeoutExpiredError: Raised when a command execution reaches
        its timeout.
    ExecuteError: General exception for command execution errors.
"""

import os
import json
import shlex
import subprocess
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Tuple,
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
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError

from openvair import config
from openvair.libs.log import get_logger
from openvair.models.execution_result import ExecutionResult

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


class UnknownArgumentError(Exception):
    """Raised when an unknown argument is passed to a function."""

    def __init__(self, message: Optional[str] = None):
        """Initialize the UnknownArgumentError.

        Args:
            message (Optional[str]): An optional error message to provide
                context for the exception.
        """
        super(UnknownArgumentError, self).__init__(message)


class NoRootWrapSpecifiedError(Exception):
    """Raised when a command requests root but no root helper is specified."""

    def __init__(self, message: Optional[str] = None):
        """Initialize the NoRootWrapSpecifiedError.

        Args:
            message (Optional[str]): An optional error message to provide
                context for the exception.
        """
        super(NoRootWrapSpecifiedError, self).__init__(message)


class ExecuteTimeoutExpiredError(Exception):
    """Raised when a command execution reaches its timeout."""

    def __init__(self, message: Optional[str] = None):
        """Initialize the ExecuteTimeoutExpiredError.

        Args:
            message (Optional[str]): An optional error message to provide
                context for the exception.
        """
        super(ExecuteTimeoutExpiredError, self).__init__(message)


class ExecuteError(Exception):
    """General exception for command execution errors."""

    def __init__(self, message: Optional[str] = None):
        """Initialize the ExecuteError.

        Args:
            message (Optional[str]): An optional error message to provide
                context for the exception.
        """
        super(ExecuteError, self).__init__(message)


def execute(*cmd: str, **kwargs: Any) -> Tuple[str, str]:  # noqa: C901 ANN401 need refact this method TODO need to parameterize the arguments correctly, in accordance with static typing
    """Runs a shell command and returns the output.

    Args:
        *cmd: Command and arguments to run.
        kwargs: Additional options for command execution, such as shell,
            run_as_root, root_helper, and timeout.

    Returns:
        Tuple[str, str]: A tuple containing the stdout and stderr output.

    Raises:
        UnknownArgumentError: If unknown keyword arguments are passed.
        NoRootWrapSpecifiedError: If run_as_root is True and no root helper is
            specified.
        ExecuteTimeoutExpiredError: If the command execution reaches its
            timeout.
        OSError: If an OS-level error occurs during command execution.
    """
    shell = kwargs.pop('shell', True)
    run_as_root = kwargs.pop('run_as_root', False)
    root_helper = kwargs.pop('root_helper', 'sudo')
    timeout = kwargs.pop('timeout', None)
    if kwargs:
        raise UnknownArgumentError('Got unknown keyword args: %r' % kwargs)

    if run_as_root and hasattr(os, 'geteuid') and os.geteuid() != 0:
        if not root_helper:
            msg = 'Command requested root, but did not specify a root helper.'
            raise NoRootWrapSpecifiedError(msg)
        if shell:
            cmd = [' '.join((root_helper, cmd[0]))] + list(cmd[1:])  # type: ignore # noqa: RUF005 need refact this method
        else:
            cmd = [shlex.split(root_helper) + list(cmd)]  # type: ignore
    cmd = ' '.join(map(str, cmd))  # type: ignore
    try:
        LOG.info('Running cmd (subprocess): %s' % cmd)
        _pipe = subprocess.PIPE

        proc = subprocess.Popen(  # noqa: S603 need refact this method
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        try:
            result = proc.communicate(timeout=timeout)
            proc.stdin.close()  # type: ignore
            LOG.info('CMD "%s" returned: %s', cmd, proc.returncode)
            if result is not None:
                (stdout, stderr) = result
                stdout = os.fsdecode(stdout)  # type: ignore
                stderr = os.fsdecode(stderr)  # type: ignore
                return stdout, stderr  # type: ignore
        except subprocess.TimeoutExpired as _:
            LOG.info('CMD "%s" reached timeout', cmd)
            raise ExecuteTimeoutExpiredError
        else:
            return result
    except OSError as err:
        message = 'Got an OSError\ncommand: %(cmd)r\nerrno: %(errno)r'
        LOG.info(message, {'cmd': cmd, 'errno': err.errno})
        raise


def terminate_process(proc: subprocess.Popen, cmd_str: str) -> str:
    """Attempts to gracefully terminate a subprocess and force kill it if fails.

    Args:
        proc (subprocess.Popen): The subprocess to be terminated.
        cmd_str (str): The command string representing the subprocess for
            logging purposes.

    Returns:
        str: The standard error output (stderr) collected from the subprocess
            after termination.
    """
    LOG.warning(f"Command '{cmd_str}' timed out. Terminating process.")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        LOG.error(f"Command '{cmd_str}' did not terminate. Killing it.")
        proc.kill()
    _, stderr = proc.communicate()
    return str(stderr)


def __run_command(
    proc: subprocess.Popen,
    cmd_str: str,
    timeout: Optional[float],
    *,
    raise_on_error: bool,
) -> ExecutionResult:
    """Handles the execution of a subprocess and processes its results.

    Args:
        proc (subprocess.Popen): The subprocess to be executed.
        cmd_str (str): The string representation of the command being executed.
        timeout (Optional[float]): Maximum time in seconds to wait for the
            command to complete. Defaults to None (no timeout).
        raise_on_error (bool): If True, raises an exception if the command exits
            with a non-zero return code. If False, includes the return code
            in the output for manual handling.

    Returns:
        ExecutionResult: An object containing the following fields:
            - returncode (int): The exit code of the command.
            - stdout (str): Standard output of the command.
            - stderr (str): Standard error output of the command.

    Raises:
        ExecuteTimeoutExpiredError: Raised if the command execution exceeds the
            specified timeout.
        ExecuteError: Raised if the command exits with a non-zero return code
            and raise_on_error is True.
    """
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        returncode = proc.returncode
        LOG.info(f"Command '{cmd_str}' completed with return code {returncode}")
        if raise_on_error and returncode != 0:
            message = (
                f"Command '{cmd_str}' failed with return code {returncode}"
            )
            LOG.error(message)
            raise ExecuteError(message)

        return ExecutionResult(
            returncode=returncode,
            stdout=stdout or '',
            stderr=stderr or '',
        )

    except subprocess.TimeoutExpired:
        stderr = terminate_process(proc, cmd_str)

        LOG.warning(
            f"Command '{cmd_str}' timed out. Attempting graceful termination."
        )
        proc.terminate()  # soft terminate
        try:
            proc.wait(timeout=5)  # 5 seconds for graceful termination
        except subprocess.TimeoutExpired:
            LOG.error(f"Command '{cmd_str}' did not terminate. Killing it now.")
            proc.kill()  # kill process after 5 seconds if not terminated
        _, stderr = proc.communicate()  # Get stderr after finishing process
        message = (
            f"Command '{cmd_str}' timed out and was killed.\n"
            f'Error: {stderr.decode()}'
        )
        raise ExecuteTimeoutExpiredError(message)


def execute_command(
    *args: str,
    shell: bool = False,
    run_as_root: bool = False,
    root_helper: str = 'sudo',
    timeout: Optional[float] = None,
    raise_on_error: bool = False,
) -> ExecutionResult:
    """Executes a shell command and returns its stdout, stderr, and exit code.

    Args:
        *args (str): The command and its arguments to execute. Each argument
            must be passed as a separate string.
        shell (bool): If True, the command will be executed through the shell.
            Defaults to False.
        run_as_root (bool): If True, the command will be executed with root
            privileges using the specified root_helper. Defaults to False.
        root_helper (str): The command used to elevate privileges, such as
            'sudo'. Defaults to 'sudo'.
        timeout (Optional[float]): Maximum time in seconds to wait for the
            command to complete. Defaults to None (no timeout).
        raise_on_error (bool): If True, raises an exception if the command exits
            with a non-zero return code. If False, includes the return code
            in the output dictionary for manual handling. Defaults to False.

    Returns:
        Dict[str, Union[str, int]]: A dictionary containing the following keys:
            - 'stdout': Standard output of the command (str).
            - 'stderr': Standard error output of the command (str).
            - 'returncode': The exit code of the command (int). This is included
                only if raise_on_error is False.

    Raises:
        ExecuteTimeoutExpiredError: Raised if the command execution exceeds the
            specified timeout.
        ExecuteError: Raised if the command exits with a non-zero return code
            and raise_on_error is True.
        OSError: Raised for system-level errors, such as command not found or
            permission issues.

    Example:
        >>> execute2('ls', '-l', raise_on_error=True)
        {'stdout': 'output', 'stderr': '', 'returncode': 0}

        >>> execute2('false', raise_on_error=True)
        Traceback (most recent call last):
            ...
        ExecuteError: Command 'false' failed

        >>> result = execute2('false', raise_on_error=False)
        >>> print(result)
        {'stdout': '', 'stderr': '', 'returncode': 1}
    """
    cmd: List[str] = list(args)
    if run_as_root and hasattr(os, 'geteuid') and os.geteuid() != 0:
        cmd = [root_helper, *cmd]

    cmd_str = ' '.join(cmd)
    LOG.info(f'Executing command: {cmd_str}')
    try:
        with subprocess.Popen(  # noqa: S603
            cmd_str if shell else cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
        ) as proc:
            return __run_command(
                proc,
                cmd_str,
                timeout,
                raise_on_error=raise_on_error,
            )
    except OSError as err:
        LOG.error(f"OS error for command '{cmd_str}': {err}")
        raise


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


def is_superuser(user: Dict = Depends(get_current_user)) -> Dict:
    """Checks if the current user is a superuser.

    Args:
        user (Dict): The user object retrieved from the JWT token.

    Returns:
        Dict: The user object if the user is a superuser.

    Raises:
        HTTPException: If the user is not a superuser.
    """
    if not user.get('is_superuser'):
        raise HTTPException(status_code=403, detail='Not enough permissions')
    return user


def get_block_devices_info() -> List[Dict[str, str]]:
    """Retrieves information about block devices on the system.

    Uses the 'lsblk' command to gather details about block devices.

    Returns:
        List[Dict[str, str]]: A dictionary containing information about block
            devices.
    """
    res, _ = execute(
        'lsblk', '-bp', '-io', 'NAME,SIZE,TYPE,MOUNTPOINT,UUID,FSTYPE', '--json'
    )
    result: List[Dict[str, str]] = json.loads(res)['blockdevices']
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
        execute(  # noqa: S604 need refact ececute
            'for i in /sys/class/fc_host/*; do sudo sh -c "echo 1 > $i/issue_lip"; done',  # noqa: E501 because need one line command for better readability
            shell=True,
            run_as_root=True,
        )
    except OSError as e:
        # Handle any errors accessing or writing to the file
        msg = (
            f'Error accessing or writing to /sys/class/fc_host/*/issue_lip: {e}'
        )
        raise OSError(msg)


def get_size(file_path: str) -> int:
    """Returns the size of the specified file.

    Args:
        file_path (str): The path of the file to check.

    Returns:
        int: The size of the file in bytes.
    """
    return Path(file_path).stat().st_size


def validate_objects(  # noqa: C901, PLR0912 because need to check the need for this function as a whole
    objects: List,
    pydantic_schema: type,
    skip_corrupted_object: bool = True,  # noqa: FBT001, FBT002 because need to check the need for this function as a whole
) -> List:
    """Validates a list of objects against a Pydantic schema.

    Args:
        objects (List): The list of objects to validate.
        pydantic_schema (type): The Pydantic schema to validate against.
        skip_corrupted_object (bool): Whether to skip corrupted objects.

    Returns:
        List: A list of validated objects.

    Raises:
        TypeError, ValueError, AssertionError: If validation fails and
            `skip_corrupted_object` is False.
    """
    result = []
    for _object in objects:
        try:
            result.append(pydantic_schema(**_object))
        except (TypeError, ValueError, AssertionError) as err:
            message = (
                f'Catch error: {err.__class__.__name__}\n {err!s}\n while '
                f'validating object: {_object} with '
                f'pydantic schema: {pydantic_schema.__class__.__name__}.'
            )
            if skip_corrupted_object:
                LOG.warning(message)
                data_for_pydantic = {}
                for key, field in pydantic_schema.__fields__.items():  # type: ignore
                    if key == 'id':
                        data_for_pydantic.update({key: _object.get('id')})
                        continue
                    elif key == 'status':  # noqa: RET507 because need to check the need for this function as a whole
                        data_for_pydantic.update({key: 'corrupted object'})
                        continue

                    if isinstance(field.type_, type):
                        value: Any
                        if issubclass(field.type_, str):
                            value = ''
                        elif issubclass(field.type_, int):
                            value = 0
                        elif issubclass(field.type_, dict):
                            value = {}
                        elif issubclass(field.type_, list):
                            value = []
                        elif issubclass(field.type_, BaseModel):
                            value = field.type_(**_object.get(key))
                        else:
                            value = None
                        data_for_pydantic.update({key: value})
                result.append(pydantic_schema(**data_for_pydantic))
            else:
                LOG.error(message)
                raise
    return result


def get_virsh_list() -> Dict:
    """Retrieves a list of virtual machines from virsh.

    Uses the 'virsh list' command to gather details about running VMs.

    Returns:
        Dict: A dictionary containing the names and power states of running VMs.
    """
    res, _ = execute('virsh', 'list')
    vms = {}
    rows = res.split('\n')[2:-2]
    for row in rows:
        _, vm_name, power_state = row.split()
        vms.update({vm_name: power_state})
    return vms


def regex_matcher(value: str) -> str:
    """Returns regex patterns for various types of values.

    Args:
        value (str): The type of value to match (e.g., 'mac_address', 'uuid4').

    Returns:
        str: The regex pattern for the specified value type.
    """
    regex_dict = {
        'mac_address': r'^([0-9A-F]{2}:){5}[0-9A-F]{2}',
        'uuid4': r'[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}$',  # noqa: E501 because its regex pattern
        'special_characters': r'(?=.*[ -\/:-@\[-\`{-~]{1,})',
    }
    return regex_dict[value]


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
