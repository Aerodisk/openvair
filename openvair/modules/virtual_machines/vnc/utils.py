"""Helpers for managing websockify/noVNC processes used in VNC sessions.

This module provides utility functions for starting websockify processes and
identifying candidate processes related to websockify/noVNC by inspecting
running system processes.

It is used internally by the VNCManager to launch and restore web-based VNC
sessions.

Functions:
    start_websockify_process: Launches a websockify process with given ports.
    get_novnc_websockify_candidate: Detects a running process that matches
        expected websockify/noVNC command line patterns.

Attributes:
    LOG: Module-level logger instance for logging process activity.
"""

from typing import Optional

import psutil

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.virtual_machines.config import (
    VNC_WS_PORT_END,
    VNC_WS_PORT_START,
)
from openvair.modules.virtual_machines.vnc.exceptions import (
    VncSessionStartupError,
)

LOG = get_logger(__name__)


def start_websockify_process(
    vm_name: str,
    vnc_host: str,
    vnc_port: int,
    ws_port: int,
) -> None:
    """Start a detached websockify process to expose VNC over WebSocket.

    Executes the `websockify` command in detached mode with `--run-once` flag
    to expose the given VNC host/port on a WebSocket port. Designed to work
    with the noVNC frontend.

    Args:
        vm_name (str): The virtual machine name used for logging.
        vnc_host (str): The hostname or IP address of the VNC server.
        vnc_port (int): The TCP port number of the VNC server (e.g., 5900).
        ws_port (int): The WebSocket port to listen on (e.g., 6100).

    Raises:
        VncSessionStartupError: If the websockify process fails to start due
            to execution failure or invalid parameters.
    """
    LOG.info(
        f'Starting VNC for VM {vm_name}: '
        f'{vnc_host}:{vnc_port} -> ws:{ws_port}'
    )

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
    except ExecuteError as e:
        error_msg = f'Failed to start websockify for VM {vm_name}: {e}'
        LOG.error(error_msg)
        raise VncSessionStartupError(error_msg) from e


def get_novnc_websockify_candidate(
    proc: psutil.Process,
) -> Optional[int]:
    """Check if a process is a websockify/noVNC instance and extract its port.

    Inspects the command line of a running process to determine whether it
    matches known patterns for a `websockify` or `noVNC` server. If a valid
    VNC WebSocket port is found in the command line arguments and falls within
    the configured VNC port range, it is returned.

    Args:
        proc (psutil.Process): A process instance from psutil.

    Returns:
        Optional[int]: The detected WebSocket port number if the process is a
        websockify/noVNC candidate, otherwise None.
    """
    info = proc.info
    cmdline = info.get('cmdline') or []
    text = ' '.join(map(str, cmdline)).lower()
    if not text or 'websockify' not in text or 'novnc' not in text:
        return None

    tokens_lc = [str(a).lower() for a in cmdline]
    if not any('websockify' in t for t in tokens_lc) and not any(
        'novnc' in t for t in tokens_lc
    ):
        return None

    for arg in cmdline:
        if arg.isdigit() and VNC_WS_PORT_START <= int(arg) <= VNC_WS_PORT_END:
            return int(arg)

    return None
