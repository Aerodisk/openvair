"""Simplified thread-safe VNC port management.

This module provides a lightweight and robust solution for managing VNC
websockify processes and port allocation. It replaces complex legacy VNC
systems with a simple, maintainable approach.

Key Features:
    - Thread-safe port allocation within configured range
    - Automatic state restoration from running processes
    - Dead process cleanup and resource management
    - Race condition protection with retry logic
    - Session lifecycle management with --run-once optimization
    - Singleton pattern for system-wide consistency

Architecture:
    The VncManager class uses a singleton pattern to ensure consistent state
    across the application. It maintains in-memory tracking of allocated ports
    and active sessions, with automatic synchronization to system reality.

Example:
    >>> from openvair.modules.virtual_machines.vnc import start_vnc_session
    >>> result = start_vnc_session('vm-123', 'localhost', 5900)
    >>> print(result['url'])  # http://server:6100/vnc.html?host=server&port=6100

Author: OpenVair Development Team
Version: 2.0 (Simplified)
"""

import socket
import threading
from typing import Set, Dict, Optional

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import (
    UnsuccessReturnCodeError,
    ExecuteTimeoutExpiredError,
)
from openvair.modules.virtual_machines.config import (
    SERVER_IP,
    VNC_WS_PORT_END,
    VNC_WS_PORT_START,
)

from .exceptions import (
    VncPortAllocationError,
    VncSessionStartupError,
    VncProcessNotFoundError,
)

LOG = get_logger(__name__)
MIN_PS_AUX_COLUMNS = 11


class VncManager:
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

    Example:
        >>> manager = VncManager()
        >>> session = manager.start_vnc_session('vm-123', 'localhost', 5900)
        >>> print(session['url'])  # VNC access URL
        >>> success = manager.stop_vnc_session('vm-123')
    """

    _instance: Optional['VncManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'VncManager':
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

        Sets up internal data structures, creates thread locks, and restores
        state from any existing websockify processes. This method is idempotent
        and will only initialize once per singleton instance.

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

    def _is_port_free(self, port: int) -> bool:
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
        for port in range(VNC_WS_PORT_START, VNC_WS_PORT_END + 1):
            # Skip if already allocated in memory
            if port in self._allocated_ports:
                continue

            # Double-check it's actually free
            if self._is_port_free(port):
                return port

        # No ports available
        total_ports = VNC_WS_PORT_END - VNC_WS_PORT_START + 1
        used_ports = len(self._allocated_ports)
        msg = (
            f'No free VNC ports available. '
            f'Used: {used_ports}/{total_ports}. '
            f'Try stopping unused VNC sessions.'
        )
        raise VncPortAllocationError(msg)

    def start_vnc_session(  # noqa: C901
        self, vm_id: str, vnc_host: str, vnc_port: int
    ) -> Dict[str, str]:
        """Start VNC session with automatic port allocation.

        Args:
            vm_id: VM identifier
            vnc_host: VNC server host (usually 'localhost')
            vnc_port: VNC server port (e.g., 5900)

        Returns:
            Dict with 'url', 'ws_port', 'pid'

        Raises:
            RuntimeError: If port allocation or websockify startup fails
        """
        with self._port_lock:
            self.cleanup_dead_sessions()

            if vm_id in self._vm_sessions:
                existing = self._vm_sessions[vm_id]
                LOG.info(
                    f'VNC session already exists for VM {vm_id}, stopping old '
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
                    LOG.info(
                        f'Terminated old websockify process {existing["pid"]}'
                    )
                except (UnsuccessReturnCodeError, ExecuteTimeoutExpiredError):
                    msg = f'Failed to terminate old process {existing["pid"]}'
                    LOG.warning(msg)

                # Cleanup old session data
                self._allocated_ports.discard(existing['ws_port'])
                del self._vm_sessions[vm_id]

            # Find and allocate free port
            ws_port = self._find_free_port()
            self._allocated_ports.add(ws_port)

            LOG.info(
                f'Starting VNC for VM {vm_id}: '
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

                pid = self._find_process_by_port(ws_port)
                if not pid:
                    msg = f'Failed to find websockify PID for port {ws_port}'
                    LOG.error(msg)
                    raise VncProcessNotFoundError(msg)  # noqa: TRY301 TODO: why?

                url = f'http://{SERVER_IP}:{ws_port}/vnc.html?host={SERVER_IP}&port={ws_port}'

                session_info = {
                    'ws_port': ws_port,
                    'vnc_host': vnc_host,
                    'vnc_port': vnc_port,
                    'pid': pid,
                    'url': url,
                }
                self._vm_sessions[vm_id] = session_info

                LOG.info(f'Started VNC for VM {vm_id}: {url}')
                return {
                    'url': url,
                    'ws_port': str(ws_port),
                    'pid': str(pid),
                }
            except UnsuccessReturnCodeError as e:
                # Cleanup on failure
                self._allocated_ports.discard(ws_port)
                error_msg = f'Failed to start websockify for VM {vm_id}: {e}'
                LOG.error(error_msg)
                raise VncSessionStartupError(error_msg) from e
            except Exception as e:
                # Cleanup on any other failure
                self._allocated_ports.discard(ws_port)
                LOG.error(f'Unexpected error starting VNC for VM {vm_id}: {e}')
                raise

    def cleanup_dead_sessions(self) -> int:
        """Clean up sessions whose processes have died.

        Note: This method assumes the _port_lock is already held.

        Returns:
            int: Number of cleaned up sessions
        """
        dead_sessions = []
        for vm_id, session in self._vm_sessions.items():
            pid = session['pid']
            try:
                execute(
                    'kill',
                    '-0',
                    str(pid),
                    params=ExecuteParams(timeout=5.0, raise_on_error=True),
                )
            except (UnsuccessReturnCodeError, ExecuteTimeoutExpiredError):
                dead_sessions.append(vm_id)
                self._allocated_ports.discard(session['ws_port'])
                LOG.info(
                    f'Cleaning up dead VNC session for VM {vm_id} (PID {pid})'
                )

        for vm_id in dead_sessions:
            del self._vm_sessions[vm_id]

        if dead_sessions:
            LOG.info(f'Cleaned up {len(dead_sessions)} dead VNC sessions')

        return len(dead_sessions)

    def stop_vnc_session(self, vm_id: str) -> bool:
        """Stop VNC session and cleanup resources.

        Args:
            vm_id: VM identifier

        Returns:
            bool: True if session was found and stopped
        """
        with self._port_lock:
            if vm_id not in self._vm_sessions:
                LOG.warning(f'No VNC session found for VM {vm_id}')
                return False

            session = self._vm_sessions[vm_id]
            ws_port = session['ws_port']
            pid = session['pid']

            LOG.info(
                f'Stopping VNC session for VM {vm_id} (port {ws_port}, '
                f'PID {pid})'
            )

            success = True

            # Kill the process
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
            del self._vm_sessions[vm_id]

            LOG.info(f'VNC session cleanup completed for VM {vm_id}')
            return success

    def _restore_state_from_system(self) -> None:
        """Restore VNC manager state from running websockify processes.

        This method scans for running websockify processes in the VNC port range
        and rebuilds the in-memory state to match the system reality.
        """
        LOG.info('Restoring VNC Manager state from running processes...')

        try:
            result = execute('ps', 'aux', params=ExecuteParams(timeout=10.0))
            restored_count = self._parse_ps_output(result.stdout)
            self._log_restore_result(restored_count)
        except (UnsuccessReturnCodeError, ExecuteTimeoutExpiredError) as e:
            LOG.warning(f'Failed to restore VNC Manager state: {e}')

    def _parse_ps_output(self, ps_output: str) -> int:
        """Parse ps aux output and restore websockify processes.

        Args:
            ps_output: Output from 'ps aux' command

        Returns:
            Number of restored processes
        """
        restored_count = 0
        for line in ps_output.split('\n'):
            if not self._is_websockify_line(line):
                continue

            ws_port = self._extract_port_from_line(line)
            if ws_port:
                self._allocated_ports.add(ws_port)
                pid = self._extract_pid_from_line(line)
                LOG.debug(f'Restored websockify: PID {pid}, port {ws_port}')
                restored_count += 1

        return restored_count

    def _is_websockify_line(self, line: str) -> bool:
        """Check if a ps aux line contains a websockify process.

        Filters for lines that contain both 'websockify' and 'noVNC' to ensure
        we only match our VNC websockify processes, not other websockify
        instances.

        Args:
            line: Single line from ps aux output

        Returns:
            bool: True if line contains websockify process, False otherwise
        """
        return 'websockify' in line and 'noVNC' in line

    def _extract_pid_from_line(self, line: str) -> Optional[int]:
        """Extract process ID from a ps aux output line.

        Parses the PID from the second column of ps aux output after validating
        the line has the minimum expected number of columns.

        Args:
            line: Single line from ps aux output

        Returns:
            Optional[int]: Process ID if found, None otherwise
        """
        try:
            parts = line.split()
            return int(parts[1]) if len(parts) >= MIN_PS_AUX_COLUMNS else None
        except (ValueError, IndexError):
            return None

    def _extract_port_from_line(self, line: str) -> Optional[int]:
        """Extract websockify port number from ps aux command line.

        Searches through command line arguments (starting from column 11) to
        find
        a numeric argument that falls within the configured VNC port range.

        Args:
            line: Single line from ps aux output

        Returns:
            Optional[int]: Port number if found in range, None otherwise

        Note:
            Only considers ports within VNC_WS_PORT_START to VNC_WS_PORT_END
            range
        """
        try:
            parts = line.split()
            if len(parts) < MIN_PS_AUX_COLUMNS:
                return None

            # Look for port in command arguments (parts[11:])
            for part in parts[11:]:
                if (
                    part.isdigit()
                    and VNC_WS_PORT_START <= int(part) <= VNC_WS_PORT_END
                ):
                    return int(part)
        except (ValueError, IndexError):
            pass
        return None

    def _log_restore_result(self, restored_count: int) -> None:
        """Log the outcome of state restoration process.

        Provides appropriate log messages based on whether any websockify
        processes were found and restored to the manager's state.

        Args:
            restored_count: Number of processes successfully restored
        """
        if restored_count > 0:
            msg = (
                f'Restored {restored_count} websockify processes '
                f'to VNC Manager state'
            )
            LOG.info(msg)
        else:
            LOG.info('No existing websockify processes found')

    def _find_process_by_port(self, port: int) -> Optional[int]:
        """Find the process ID listening on a specific port.

        Uses lsof to identify which process is currently listening on the
        specified port. This is used to track websockify PIDs after startup.

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

    def get_stats(self) -> Dict:
        """Get current VNC manager statistics.

        Returns comprehensive statistics about port usage and active sessions
        for monitoring and debugging purposes.

        Returns:
            Dict: Statistics containing:
                - total_ports: Total ports in configured range
                - used_ports: Number of currently allocated ports
                - free_ports: Number of available ports
                - active_sessions: Number of active VM sessions
                - port_range: String representation of port range
        """
        with self._port_lock:
            total_ports = VNC_WS_PORT_END - VNC_WS_PORT_START + 1
            used_ports = len(self._allocated_ports)
            return {
                'total_ports': total_ports,
                'used_ports': used_ports,
                'free_ports': total_ports - used_ports,
                'active_sessions': len(self._vm_sessions),
                'port_range': f'{VNC_WS_PORT_START}-{VNC_WS_PORT_END}',
            }


# Global singleton instance
vnc_manager = VncManager()


# Convenience functions for easy integration with the global VNC manager
# instance
def start_vnc_session(
    vm_id: str, vnc_host: str, vnc_port: int
) -> Dict[str, str]:
    """Start a VNC session for the specified virtual machine.

    This convenience function provides direct access to the global VNC manager
    instance for starting VNC sessions without needing to manage the singleton.

    Args:
        vm_id: Unique identifier for the virtual machine
        vnc_host: Hostname or IP where the VM's VNC server is running
        vnc_port: Port number of the VM's VNC server (typically 5900+)

    Returns:
        Dict containing:
            - url: Complete noVNC access URL for the browser
            - ws_port: WebSocket port allocated for this session
            - pid: Process ID of the websockify daemon

    Raises:
        VncPortAllocationError: When no free ports are available
        VncSessionStartupError: When websockify process fails to start
        VncProcessNotFoundError: When websockify PID cannot be determined

    Example:
        >>> session = start_vnc_session('vm-001', 'localhost', 5900)
        >>> print(f"VNC URL: {session['url']}")
        VNC URL: http://server:6100/vnc.html?host=server&port=6100
    """
    return vnc_manager.start_vnc_session(vm_id, vnc_host, vnc_port)


def stop_vnc_session(vm_id: str) -> bool:
    """Stop the VNC session for the specified virtual machine.

    This convenience function provides direct access to the global VNC manager
    for stopping VNC sessions and cleaning up associated resources.

    Args:
        vm_id: Unique identifier for the virtual machine

    Returns:
        bool: True if session was found and successfully stopped, False if
              no session existed for the given VM ID

    Note:
        This function attempts graceful termination (SIGTERM) first, followed
        by forced termination (SIGKILL) if necessary. Resources are cleaned up
        regardless of termination success.

    Example:
        >>> success = stop_vnc_session('vm-001')
        >>> if success:
        ...     print("VNC session stopped successfully")
    """
    return vnc_manager.stop_vnc_session(vm_id)


def get_vnc_stats() -> Dict:
    """Get current statistics from the VNC manager.

    This convenience function provides direct access to VNC manager statistics
    for monitoring port usage and active sessions.

    Returns:
        Dict containing current statistics:
            - total_ports: Total number of ports in the configured range
            - used_ports: Number of currently allocated ports
            - free_ports: Number of available ports remaining
            - active_sessions: Number of active VM VNC sessions
            - port_range: String representation of the port range
              (e.g., "6100-6999")

    Example:
        >>> stats = get_vnc_stats()
        >>> print(f"Port usage: {stats['used_ports']}/{stats['total_ports']}")
        >>> print(f"Active sessions: {stats['active_sessions']}")
        Port usage: 5/900
        Active sessions: 3
    """
    return vnc_manager.get_stats()
