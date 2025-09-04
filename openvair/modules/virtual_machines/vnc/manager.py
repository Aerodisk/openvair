"""Thread-safe VNC port and session manager.

This module provides a simplified and robust system for managing
websockify-based VNC sessions in a concurrent environment. It
includes automatic restoration of state from system processes and performs
reliable cleanup of dead sessions.

Classes:
    VNCManager: Singleton-based class for managing websockify VNC sessions.

Functions:
    None (use utils.py for process-related helpers).

Attributes:
    LOG: Logger instance for VNC session management.

# Example:
#     >>> from openvair.modules.virtual_machines.vnc.manager import VNCManager
#     >>> manager = VNCManager()
#     >>> session = manager.start_vnc_session('vm-123', 'localhost', 5900)
#     >>> print(session['url'])  # Access URL
"""

import socket
import threading
from typing import Set, Dict, Optional

import psutil

from openvair.libs.log import get_logger
from openvair.libs.processes import find_process_by_port
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import (
    ExecuteError,
    UnsuccessReturnCodeError,
    ExecuteTimeoutExpiredError,
)
from openvair.modules.virtual_machines.config import (
    SERVER_IP,
    VNC_WS_PORT_END,
    VNC_WS_PORT_START,
)
from openvair.modules.virtual_machines.vnc.utils import (
    start_websockify_process,
    get_novnc_websockify_candidate,
)
from openvair.modules.virtual_machines.vnc.exceptions import (
    VncPortAllocationError,
)

LOG = get_logger(__name__)


class VNCManager:
    """Thread-safe VNC port manager with automatic state restoration.

    This class manages VNC websockify processes and port allocation using a
    singleton pattern to ensure system-wide consistency. It automatically
    handles:

    - Port allocation and deallocation within the configured range
    - Dead process cleanup and resource management
    - State synchronization with running system processes
    - Thread-safe operations with proper locking

    Attributes:
        _instance: Singleton instance reference
        _lock: Class-level lock for singleton creation
        _port_lock: Instance-level lock for port operations
        _allocated_ports: Set of currently allocated websockify ports
        _vm_sessions: Dict mapping VM IDs to session information
        _initialized: Flag to prevent multiple initialization

    # Example:
    #     >>> manager = VncManager()
    #     >>> session = manager.start_vnc_session('vm-123', 'localhost', 5900)
    #     >>> print(session['url'])  # VNC access URL
    #     >>> success = manager.stop_vnc_session('vm-123')
    """

    _instance: Optional['VNCManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'VNCManager':
        """Create singleton instance with thread safety.

        Implements the singleton pattern to ensure only one VncManager instance
        exists throughout the application lifecycle. Uses double-checked locking
        to prevent race conditions during instance creation.

        Returns:
            VncManager: The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the VNC manager with state restoration.

        Sets up internal locks and data structures for managing VNC sessions.
        Performs a system scan to restore existing websockify state.

        This method is idempotent and executes only once per singleton instance.

        Side Effects:
            - Creates thread locks for port operations
            - Initializes port and session tracking structures
            - Scans for existing websockify processes
            - Logs initialization status
        """
        if not hasattr(self, '_initialized'):
            self._port_lock = threading.Lock()
            self._allocated_ports: Set[int] = set()
            self._vm_sessions: Dict[str, Dict] = {}
            self._initialized = True
            LOG.info('Simple VNC Manager initialized')
            self._restore_state_from_system()

    def start_vnc_session(
        self,
        vm_name: str,
        vnc_host: str,
        vnc_port: int,
    ) -> Dict[str, str]:
        """Start VNC session with automatic port allocation.

        Allocates a free WebSocket port and starts a websockify process
        connected to the specified VNC server. Registers the session and
        returns connection details.

        Args:
            vm_name (str): The virtual machine name.
            vnc_host (str): VNC server host (usually 'localhost').
            vnc_port (int): VNC server port (e.g., 5900).

        Returns:
            Dict[str, str]: Dictionary containing:
                - 'url': URL to access noVNC client.
                - 'ws_port': Allocated WebSocket port.
                - 'pid': Process ID of the websockify process.

        Raises:
            ExecuteError: If websockify process fails to start.
        """
        with self._port_lock:
            self.cleanup_dead_sessions()
            self._cleanup_existing_session_resources(vm_name)

            ws_port = self._find_free_port()
            self._allocated_ports.add(ws_port)

            try:
                start_websockify_process(
                    vm_name,
                    vnc_host,
                    vnc_port,
                    ws_port,
                )
                pid = find_process_by_port(ws_port)

            except ExecuteError:
                self._allocated_ports.discard(ws_port)
                raise

            session_info = {
                'ws_port': ws_port,
                'vnc_host': vnc_host,
                'vnc_port': vnc_port,
                'pid': pid,
                'url': f'http://{SERVER_IP}:{ws_port}/vnc.html?host={SERVER_IP}&port={ws_port}',
            }
            self._vm_sessions[vm_name] = session_info

            LOG.info(f'Started VNC for VM {vm_name}: {session_info["url"]}')
            return {
                'url': str(session_info['url']),
                'ws_port': str(ws_port),
                'pid': str(pid),
            }

    def cleanup_dead_sessions(self) -> int:
        """Clean up sessions whose processes are no longer running.

        Scans session registry and removes entries for which the process no
        longer exists using `psutil.pid_exists`.

        Returns:
            int: Number of cleaned up sessions.
        """
        dead_sessions = []
        for vm_name, session in self._vm_sessions.items():
            pid = session['pid']
            if not psutil.pid_exists(pid):
                dead_sessions.append(vm_name)
                self._allocated_ports.discard(session['ws_port'])
                LOG.info(
                    f'Cleaning up dead VNC session for VM {vm_name} (PID {pid})'
                )

        for vm_name in dead_sessions:
            del self._vm_sessions[vm_name]

        if dead_sessions:
            LOG.info(f'Cleaned up {len(dead_sessions)} dead VNC sessions')

        return len(dead_sessions)

    def stop_vnc_session(self, vm_name: str) -> bool:
        """Stop VNC session and cleanup resources.

        Args:
            vm_name: The virtual machine name

        Returns:
            bool: True if session was found and stopped
        """
        with self._port_lock:
            if vm_name not in self._vm_sessions:
                LOG.warning(f'No VNC session found for VM {vm_name}')
                return False

            session = self._vm_sessions[vm_name]
            ws_port = session['ws_port']
            pid = session['pid']

            LOG.info(
                f'Stopping VNC session for VM {vm_name} (port {ws_port}, '
                f'PID {pid})'
            )

            success = True

            try:
                execute(
                    'kill',
                    '-TERM',
                    str(pid),
                    params=ExecuteParams(timeout=5.0, raise_on_error=True),
                )
                LOG.info(f'Terminated websockify process {pid}')
            except (UnsuccessReturnCodeError, ExecuteTimeoutExpiredError):
                try:
                    execute(
                        'kill',
                        '-KILL',
                        str(pid),
                        params=ExecuteParams(timeout=5.0, raise_on_error=True),
                    )
                    LOG.warning(f'Force killed websockify process {pid}')
                except (
                    UnsuccessReturnCodeError,
                    ExecuteTimeoutExpiredError,
                ):
                    LOG.error(f'Failed to kill websockify process {pid}')
                    success = False

            # Cleanup resources
            self._allocated_ports.discard(ws_port)
            del self._vm_sessions[vm_name]

            LOG.info(f'VNC session cleanup completed for VM {vm_name}')
            return success

    def _find_free_port(self) -> int:
        """Find the first available port in the configured VNC port range.

        Iterates through the configured port range (VNC_WS_PORT_START to
        VNC_WS_PORT_END) to find a port that is both not allocated in memory
        and actually free at the system level.

        Returns:
            int: First available port number

        Raises:
            VncPortAllocationError: When no free ports are available in range

        Note:
            This method performs both in-memory and system-level checks to
            ensure
            the port is truly available before allocation.
        """
        total_ports = VNC_WS_PORT_END - VNC_WS_PORT_START + 1
        for port in range(total_ports):
            if port not in self._allocated_ports:
                try:
                    with socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM
                    ) as sock:
                        sock.setsockopt(
                            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                        )
                        sock.bind(('localhost', port))
                        return port
                except OSError:
                    LOG.error('Failed to allocate port')

        message = (
            f'No free VNC ports available. '
            f'Used: {len(self._allocated_ports)}/{total_ports}. '
            f'Try stopping unused VNC sessions.'
        )
        raise VncPortAllocationError(message)

    def _cleanup_existing_session_resources(self, vm_name: str) -> None:
        """Clean up resources for an existing VNC session.

        Args:
            vm_name: VM name for the session to cleanup

        Note:
            Assumes _port_lock is already held by the caller.
        """
        if vm_name not in self._vm_sessions:
            return

        existing = self._vm_sessions[vm_name]
        LOG.info(
            f'VNC session already exists for VM {vm_name}, stopping old '
            f'session (port {existing["ws_port"]}, '
            f'PID {existing["pid"]})'
        )

        # Stop the old session
        # don't use stop_vnc_session to avoid lock recursion
        try:
            execute(
                'kill',
                '-TERM',
                str(existing['pid']),
                params=ExecuteParams(timeout=2.0),
            )
            LOG.info(f'Terminated old websockify process {existing["pid"]}')
        except (UnsuccessReturnCodeError, ExecuteTimeoutExpiredError):
            msg = f'Failed to terminate old process {existing["pid"]}'
            LOG.warning(msg)

        # Cleanup old session data
        self._allocated_ports.discard(existing['ws_port'])
        del self._vm_sessions[vm_name]

    def _restore_state_from_system(self) -> None:
        """Restore VNC manager state from running websockify processes.

        Uses psutil to scan for websockify processes and extract port
        information. This is more reliable than parsing ps aux output.
        """
        LOG.info('Restoring VNC Manager state from running processes...')

        restored: Set[int] = set()

        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                ws_port = get_novnc_websockify_candidate(proc)
                if ws_port is not None and ws_port not in self._allocated_ports:
                    self._allocated_ports.add(ws_port)
                    restored.add(ws_port)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
            return

        if restored:
            LOG.info(
                f'Restored {len(restored)} websockify processes to VNC Manager '
                f'state: {sorted(restored)}'
            )
        else:
            LOG.info('No existing websockify processes found')
