"""Simplified thread-safe VNC port management.

This replaces the complex 940-line VNC system with a simple ~250-line solution.
Features:
- Thread-safe port allocation
- In-memory state (no persistence)
- Automatic cleanup
- Race condition safe (retry-friendly)
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


class VncManager:
    """Simple thread-safe VNC port manager."""

    _instance: Optional['VncManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'VncManager':
        """Singleton pattern for thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the manager."""
        if not hasattr(self, '_initialized'):
            self._port_lock = threading.Lock()
            self._allocated_ports: Set[int] = set()
            self._vm_sessions: Dict[str, Dict] = {}
            self._initialized = True
            LOG.info('Simple VNC Manager initialized')

    def _is_port_free(self, port: int) -> bool:
        """Check if port is actually free by attempting to bind."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False

    def _find_free_port(self) -> int:
        """Find first free port in configured range.

        Returns:
            int: Free port number

        Raises:
            RuntimeError: No free ports available
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

    def start_vnc_session(
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
            # Check if session already exists
            if vm_id in self._vm_sessions:
                existing = self._vm_sessions[vm_id]
                msg = (
                    f'VNC session already exists for VM {vm_id}: '
                    f'{existing["url"]}'
                )
                LOG.warning(
                    f"VNC session already exists for VM {vm_id}: "
                    f"{existing['url']}"
                )
                return {
                    'url': existing['url'],
                    'ws_port': str(existing['ws_port']),
                    'pid': str(existing['pid']),
                }

            # Find and allocate free port
            ws_port = self._find_free_port()
            self._allocated_ports.add(ws_port)

            LOG.info(
                f'Starting VNC for VM {vm_id}: '
                f'{vnc_host}:{vnc_port} -> ws:{ws_port}'
            )

            try:
                # Start websockify
                execute(
                    'websockify',
                    '-D',  # daemon mode
                    '--run-once',  # exit after connection
                    '--web',
                    '/opt/aero/openvair/openvair/libs/noVNC/',
                    str(ws_port),
                    f'{vnc_host}:{vnc_port}',
                    params=ExecuteParams(raise_on_error=True),
                )

                # Find the PID
                pid = self._find_process_by_port(ws_port)
                if not pid:
                    msg = f'Failed to find websockify PID for port {ws_port}'
                    LOG.error(msg)
                    raise VncProcessNotFoundError(msg)  # noqa: TRY301 TODO: why?

                # Generate URL
                url = f'http://{SERVER_IP}:{ws_port}/vnc.html?host={SERVER_IP}&port={ws_port}'

                # Store session info
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

    def _find_process_by_port(self, port: int) -> Optional[int]:
        """Find process PID by port number."""
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
        """Get simple statistics."""
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


# Convenience functions for easy integration
def start_vnc_session(
    vm_id: str, vnc_host: str, vnc_port: int
) -> Dict[str, str]:
    """Start VNC session - convenience function."""
    return vnc_manager.start_vnc_session(vm_id, vnc_host, vnc_port)


def stop_vnc_session(vm_id: str) -> bool:
    """Stop VNC session - convenience function."""
    return vnc_manager.stop_vnc_session(vm_id)


def get_vnc_stats() -> Dict:
    """Get VNC statistics - convenience function."""
    return vnc_manager.get_stats()
