"""Thread-safe VNC port pool manager.

This module manages allocation and deallocation of WebSocket ports for VNC
sessions, ensuring no conflicts occur when multiple VMs are started
simultaneously.
"""

import json
import fcntl
import socket
import threading
from typing import Dict, Optional, Generator
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.virtual_machines.config import (
    VNC_LOCK_FILE,
    VNC_STATE_FILE,
    VNC_WS_PORT_END,
    VNC_WS_PORT_START,
)
from openvair.modules.virtual_machines.vnc.exceptions import (
    VncPortAllocationError,
    VncPortPoolExhaustedException,
)

LOG = get_logger(__name__)


class VncPortPoolManager:
    """Thread-safe manager for VNC WebSocket port allocation.

    This class manages a pool of available ports for VNC WebSocket connections,
    ensuring thread-safe allocation and deallocation operations with persistent
    state management.

    Attributes:
        _instance: Singleton instance
        _lock: Thread lock for singleton initialization
        _initialized: Initialization flag
    """

    _instance: Optional['VncPortPoolManager'] = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls) -> 'VncPortPoolManager':
        """Singleton pattern implementation.

        Returns:
            VncPortPoolManager: The singleton instance of the manager
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the port pool manager."""
        if not self._initialized:
            self._ensure_directories()
            VncPortPoolManager._initialized = True
            LOG.info('VNC Port Pool Manager initialized')

    def _ensure_directories(self) -> None:
        """Ensure required directories exist with proper permissions.

        Raises:
            VncPortAllocationError: If directory creation fails
        """
        try:
            # Create state file directory
            state_dir = Path(VNC_STATE_FILE).parent
            state_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

            # Create lock file directory
            lock_dir = Path(VNC_LOCK_FILE).parent
            lock_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

        except (OSError, PermissionError) as e:
            msg = f'Failed to create required directories: {e}'
            LOG.error(msg)
            raise VncPortAllocationError(msg)

    @contextmanager
    def _acquire_lock(self) -> Generator:
        """Acquire exclusive file lock for atomic operations.

        This method ensures thread-safe access to the port state file by
        acquiring an exclusive file lock. The lock is automatically released
        when the context manager exits.

        Yields:
            None: Context manager for exclusive access to port state

        Raises:
            VncPortAllocationError: If lock acquisition fails
        """
        lock_file = None
        try:
            # Use file-based locking with open() for simplicity
            lock_file = open(VNC_LOCK_FILE, 'a+')

            # Acquire exclusive lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            LOG.debug('Acquired VNC port pool lock')
            yield

        except (OSError, IOError) as e:
            msg = f'Failed to acquire lock: {e}'
            LOG.error(msg)
            raise VncPortAllocationError(msg)
        finally:
            if lock_file is not None:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    lock_file.close()
                    LOG.debug('Released VNC port pool lock')
                except (OSError, IOError) as e:
                    LOG.warning(f'Failed to release lock properly: {e}')

    def _load_state(self) -> Dict:
        """Load port allocation state from file.

        Returns:
            Dict: Port allocation state containing allocated_ports, free_ports,
                and last_cleanup
        """
        try:
            if not Path(VNC_STATE_FILE).exists():
                return self._create_initial_state()

            with Path(VNC_STATE_FILE).open('r') as f:
                state = json.load(f)

            # Validate state structure
            required_keys = ['allocated_ports', 'free_ports', 'last_cleanup']
            if not all(key in state for key in required_keys):
                LOG.warning('Invalid state file, recreating')
                return self._create_initial_state()
            else:
                return state

        except (json.JSONDecodeError, OSError) as e:
            LOG.warning(f'Failed to load state file: {e}, recreating')
            return self._create_initial_state()

    def _create_initial_state(self) -> Dict:
        """Create initial port pool state.

        Returns:
            Dict: Initial state with all ports marked as free
        """
        all_ports = list(range(VNC_WS_PORT_START, VNC_WS_PORT_END + 1))
        return {
            'allocated_ports': {},
            'free_ports': all_ports,
            'last_cleanup': datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self, state: Dict) -> None:
        """Save port allocation state to file.

        Args:
            state: Port allocation state to save

        Raises:
            VncPortAllocationError: If state saving fails
        """
        try:
            # Atomic write: write to temp file, then rename
            temp_file = f'{VNC_STATE_FILE}.tmp'
            with Path(temp_file).open('w') as f:
                json.dump(state, f, indent=2)

            # Atomic rename using execute
            execute(
                'mv',
                temp_file,
                VNC_STATE_FILE,
                params=ExecuteParams(raise_on_error=True),
            )

            # Set proper permissions using execute
            execute(
                'chmod',
                '644',
                VNC_STATE_FILE,
                params=ExecuteParams(raise_on_error=True),
            )

        except (OSError, IOError, ExecuteError) as e:
            LOG.error(f'Failed to save state file: {e}')
            msg = f'State save failed: {e}'
            raise VncPortAllocationError(msg) from e

    def _is_port_actually_free(self, port: int) -> bool:
        """Check if port is actually free by attempting to bind to it.

        This method validates that a port is truly available by attempting
        to create and bind a socket to it. This provides more reliable
        validation than just checking the state file.

        Args:
            port: Port number to check

        Returns:
            bool: True if port is free, False if occupied
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False

    def _validate_free_ports(self, state: Dict) -> None:
        """Validate that ports in free_ports are actually free.

        This method checks each port marked as free to ensure it's truly
        available. Ports that are marked as free but actually in use are
        removed from the free ports list.

        Args:
            state: Current state dictionary (modified in-place)
        """
        truly_free = []
        for port in state['free_ports']:
            if self._is_port_actually_free(port):
                truly_free.append(port)
            else:
                LOG.debug(
                    f'Port {port} marked as free but actually in use, '
                    'removing from pool'
                )

        state['free_ports'] = truly_free

    def allocate_port(self, vm_id: str, pid: Optional[int] = None) -> int:
        """Allocate a free port for VNC WebSocket connection.

        This method finds the first available port from the configured range
        and validates that it's actually free by attempting to bind to it.
        If no free ports are available, it attempts cleanup of stale ports
        before giving up.

        Args:
            vm_id: Unique identifier for the virtual machine
            pid: Process ID to associate with the port (optional)

        Returns:
            int: Allocated port number from the configured range

        Raises:
            VncPortPoolExhaustedException: No free ports available after cleanup
            VncPortAllocationError: System error during allocation or
                file operations
        """
        with self._acquire_lock():
            state = self._load_state()

            # Validate free ports first
            self._validate_free_ports(state)

            if not state['free_ports']:
                total_ports = VNC_WS_PORT_END - VNC_WS_PORT_START + 1  # = 900
                used_ports = len(state['allocated_ports'])
                msg = (
                    f'Все VNC порты заняты ({used_ports}/{total_ports}). '
                    'Закройте неиспользуемые VNC сессии и попробуйте снова.'
                )
                raise VncPortPoolExhaustedException(msg)

            return self._allocate_first_free_port(state, vm_id, pid)

    def _allocate_first_free_port(self, state: Dict, vm_id: str, pid: Optional[int] = None) -> int:
        """Allocate the first available port from the free ports list.

        Args:
            state: Current state dictionary
            vm_id: Virtual machine identifier
            pid: Process ID to associate with the port (optional)

        Returns:
            int: Allocated port number

        Raises:
            VncPortPoolExhaustedException: If no ports are actually free
        """
        # Find first actually free port
        for port in state['free_ports'][:]:
            if self._is_port_actually_free(port):
                # Allocate the port
                state['free_ports'].remove(port)
                state['allocated_ports'][str(port)] = {
                    'vm_id': vm_id,
                    'allocated_at': datetime.now(timezone.utc).isoformat(),
                    'pid': pid,
                }

                self._save_state(state)
                LOG.info(f'Allocated VNC port {port} for VM {vm_id}')
                return port
            # Port appears free in state but is actually occupied
            LOG.debug(
                f'Port {port} marked as free but is occupied, '
                'removing from pool'
            )
            state['free_ports'].remove(port)

        # If we get here, no ports were actually free
        self._save_state(state)
        total_ports = VNC_WS_PORT_END - VNC_WS_PORT_START + 1
        used_ports = len(state['allocated_ports'])
        msg = (
            f'Все VNC порты заняты ({used_ports}/{total_ports}). '
            'Закройте неиспользуемые VNC сессии и попробуйте снова.'
        )
        raise VncPortPoolExhaustedException(msg)

    def release_port(self, port: int, vm_id: Optional[str] = None) -> None:
        """Release a previously allocated port.

        Args:
            port: Port number to release
            vm_id: VM ID for validation (optional)
        """
        with self._acquire_lock():
            state = self._load_state()
            port_str = str(port)

            if port_str not in state['allocated_ports']:
                LOG.warning(f'Attempted to release unallocated port {port}')
                return

            # Optional VM ID validation
            if vm_id and state['allocated_ports'][port_str]['vm_id'] != vm_id:
                LOG.warning(
                    f"VM ID mismatch for port {port}: expected {vm_id}, "
                    f"got {state['allocated_ports'][port_str]['vm_id']}"
                )

            # Release the port
            del state['allocated_ports'][port_str]
            if port not in state['free_ports']:
                state['free_ports'].append(port)
                state['free_ports'].sort()

            self._save_state(state)
            LOG.info(f'Released VNC port {port}')

    def update_port_pid(self, port: int, pid: int) -> None:
        """Update PID for an allocated port.

        Args:
            port: Port number
            pid: Process ID to associate with the port
        """
        with self._acquire_lock():
            state = self._load_state()
            port_str = str(port)

            if port_str in state['allocated_ports']:
                state['allocated_ports'][port_str]['pid'] = pid
                self._save_state(state)
                LOG.debug(f'Updated port {port} with PID {pid}')

    def get_port_statistics(self) -> Dict:
        """Get current port pool statistics.

        Returns:
            Dict: Statistics about port allocation
        """
        with self._acquire_lock():
            state = self._load_state()

            total_ports = VNC_WS_PORT_END - VNC_WS_PORT_START + 1
            allocated_count = len(state['allocated_ports'])
            free_count = len(state['free_ports'])

            return {
                'total_ports': total_ports,
                'allocated_ports': allocated_count,
                'free_ports': free_count,
                'utilization_percent': (allocated_count / total_ports) * 100,
                'port_range': f'{VNC_WS_PORT_START}-{VNC_WS_PORT_END}',
            }
