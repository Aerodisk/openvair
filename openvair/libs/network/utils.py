"""Network utility functions for Open vAIR.

This module provides common network-related utilities that can be used
across different modules in the Open vAIR system.
"""

import socket
from typing import Dict, List, Optional, Set

from typing_extensions import Any

from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import (
    UnsuccessReturnCodeError,
    ExecuteTimeoutExpiredError,
)
from openvair.libs.network.exceptions import WebsockifyStartupError


def is_port_free(port: int) -> bool:
    """Check if a port is available for binding.

    Attempts to bind to the specified port to verify it's not in use.
    Uses SO_REUSEADDR to avoid issues with recently closed connections.

    Args:
        port: Port number to check

    Returns:
        bool: True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('localhost', port))
            return True
    except OSError:
        return False


def find_free_port_in_range(
    port_start: int, port_end: int, allocated_ports: Set[int]
) -> Optional[int]:
    """Find the first available port in the port range.

    Iterates through the configured port range (port_start to port_end)
    to find a port that is both not allocated in memory and actually
    free at the system level.

    Args:
        port_start: Start of the port range
        port_end: End of the port range
        allocated_ports: Set of ports that are already allocated

    Returns:
        Optional[int]: First available port number or None if no free
            port is found in the range.

    Note:
        This method performs both in-memory and system-level checks to
        ensure the port is truly available before allocation.
    """
    for port in range(port_start, port_end + 1):
        if port in allocated_ports:
            continue

        if is_port_free(port):
            return port

    return None


def find_process_id_by_port(port: int) -> Optional[int]:
    """Find the process ID listening on a specific port.

    Uses lsof to identify which process is currently listening on the
    specified port.

    Args:
        port: Port number to check

    Returns:
        Optional[int]: Process ID if found, None otherwise

    Note:
        Handles various command execution errors gracefully by returning
        None
    """
    try:
        result = execute(
            'lsof', '-ti', f':{port}', params=ExecuteParams(timeout=10.0)
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
    except (
        UnsuccessReturnCodeError,
        ExecuteTimeoutExpiredError,
        ValueError,
    ):
        pass
    return None


def start_websockify_process(
    vnc_host: str, vnc_port: int, ws_port: int
) -> None:
    """Start websockify process.

    Args:
        vnc_host: VNC server host
        vnc_port: VNC server port
        ws_port: WebSocket port to use

    Raises:
        WebsockifyStartupError: If websockify fails to start
    """
    try:
        execute(
            'websockify',
            '-D',
            '--run-once',
            '--web',
            '/opt/aero/openvair/openvair/libs/noVNC/',
            str(ws_port),
            f'{vnc_host}:{vnc_port}',
            params=ExecuteParams(raise_on_error=True),
        )
    except UnsuccessReturnCodeError as e:
        raise WebsockifyStartupError(str(e)) from e


def create_vnc_session_info(
    server_ip: str,
    ws_port: int,
    vnc_host: str,
    vnc_port: int,
    pid: int,
) -> Dict[str, Any]:
    """Create session information dictionary.

    Args:
        server_ip: Server IP address
        ws_port: WebSocket port
        vnc_host: VNC server host
        vnc_port: VNC server port
        pid: Process ID of websockify

    Returns:
        Dict containing session information
    """
    url = (
        f'http://{server_ip}:{ws_port}/vnc.html?host={server_ip}&port={ws_port}'
    )

    return {
        'ws_port': ws_port,
        'vnc_host': vnc_host,
        'vnc_port': vnc_port,
        'pid': pid,
        'url': url,
    }


def extract_port_from_cmdline_by_range(
    port_start: int,
    port_end: int,
    cmdline: list,
) -> Optional[int]:
    """Extract port number from command line arguments by range.

    Searches through command line arguments to find a numeric argument
    that falls within the configured port range.

    Args:
        port_start: Start of the port range
        port_end: End of the port range
        cmdline: List of command line arguments

    Returns:
        Optional[int]: Port number if found in range, None otherwise
    """
    for arg in cmdline:
        if arg.isdigit() and port_start <= int(arg) <= port_end:
            return int(arg)
    return None
