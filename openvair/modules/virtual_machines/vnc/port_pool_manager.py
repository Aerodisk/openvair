"""Thread-safe VNC port pool manager.

This module manages allocation and deallocation of WebSocket ports for VNC
sessions, ensuring no conflicts occur when multiple VMs are started
simultaneously.
"""

import json
import fcntl
import socket
import threading
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Generator
from contextlib import contextmanager

from openvair.libs.log import get_logger
from openvair.libs.cli.executor import execute
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.virtual_machines.config import (
    VNC_LOCK_FILE,
    VNC_STATE_FILE,
    VNC_WS_PORT_END,
    VNC_MAX_SESSIONS,
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
        """Singleton pattern implementation."""
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
        """Ensure required directories exist with proper permissions."""
        try:
            # Create state file directory
            state_dir = Path(VNC_STATE_FILE).parent
            state_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

            # Create lock file directory
            lock_dir = Path(VNC_LOCK_FILE).parent
            lock_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

        except (OSError, PermissionError) as e:
            msg = f"Failed to create required directories: {e}"
            LOG.error(msg)
            raise VncPortAllocationError(msg)

    @contextmanager
    def _acquire_lock(self) -> Generator:
        """Acquire exclusive file lock for atomic operations."""
        lock_file = None
        try:
            # Use file-based locking with open() for simplicity
            lock_file = open(VNC_LOCK_FILE, 'a+')
            
            # Acquire exclusive lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            LOG.debug('Acquired VNC port pool lock')
            yield

        except (OSError, IOError) as e:
            msg = f"Failed to acquire lock: {e}"
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
        """Load port allocation state from file."""
        try:
            if not Path(VNC_STATE_FILE).exists():
                return self._create_initial_state()

            with open(VNC_STATE_FILE, 'r') as f:
                state = json.load(f)

            # Validate state structure
            required_keys = ['allocated_ports', 'free_ports', 'last_cleanup']
            if not all(key in state for key in required_keys):
                LOG.warning('Invalid state file, recreating')
                return self._create_initial_state()

            return state

        except (json.JSONDecodeError, OSError) as e:
            LOG.warning(f'Failed to load state file: {e}, recreating')
            return self._create_initial_state()

    def _create_initial_state(self) -> Dict:
        """Create initial port pool state."""
        all_ports = list(range(VNC_WS_PORT_START, VNC_WS_PORT_END + 1))
        return {
            'allocated_ports': {},
            'free_ports': all_ports,
            'last_cleanup': datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self, state: Dict) -> None:
        """Save port allocation state to file."""
        try:
            # Atomic write: write to temp file, then rename
            temp_file = f'{VNC_STATE_FILE}.tmp'
            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)

            # Atomic rename using execute
            execute(
                'mv', temp_file, VNC_STATE_FILE,
                params=ExecuteParams(raise_on_error=True)
            )

            # Set proper permissions using execute
            execute(
                'chmod', '644', VNC_STATE_FILE,
                params=ExecuteParams(raise_on_error=True)
            )

        except (OSError, IOError, ExecuteError) as e:
            LOG.error(f'Failed to save state file: {e}')
            raise VncPortAllocationError(f'State save failed: {e}')

    def _is_port_actually_free(self, port: int) -> bool:
        """Check if port is actually free by attempting to bind to it."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False

    def allocate_port(self, vm_id: str) -> int:
        """Allocate a free port for VNC WebSocket connection.

        Args:
            vm_id: Unique identifier for the virtual machine

        Returns:
            int: Allocated port number

        Raises:
            VncPortPoolExhaustedException: No free ports available
            VncPortAllocationError: System error during allocation
        """
        with self._acquire_lock():
            state = self._load_state()

            if not state['free_ports']:
                # Try cleanup first
                self._cleanup_stale_ports(state)
                if not state['free_ports']:
                    raise VncPortPoolExhaustedException(
                        f'No free VNC ports available. '
                        f'Maximum sessions: {VNC_MAX_SESSIONS}'
                    )

            # Find first actually free port
            for port in state['free_ports'][
                :
            ]:  # Copy to avoid modification during iteration
                if self._is_port_actually_free(port):
                    # Allocate the port
                    state['free_ports'].remove(port)
                    state['allocated_ports'][str(port)] = {
                        'vm_id': vm_id,
                        'allocated_at': datetime.now(timezone.utc).isoformat(),
                        'pid': None,  # Will be set by ProcessManager
                    }

                    self._save_state(state)
                    LOG.info(f'Allocated VNC port {port} for VM {vm_id}')
                    return port
                else:
                    # Port appears free in state but is actually occupied
                    LOG.warning(
                        f'Port {port} marked as free but is occupied, removing from pool'
                    )
                    state['free_ports'].remove(port)

            # If we get here, no ports were actually free
            self._save_state(state)
            raise VncPortPoolExhaustedException(
                'All ports in pool are occupied'
            )

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

    def mark_port_in_use(self, port: int, pid: int) -> None:
        """Mark port as in use by a specific process.

        Args:
            port: Port number
            pid: Process ID of websockify
        """
        with self._acquire_lock():
            state = self._load_state()
            port_str = str(port)

            if port_str in state['allocated_ports']:
                state['allocated_ports'][port_str]['pid'] = pid
                self._save_state(state)
                LOG.debug(f'Marked port {port} as in use by PID {pid}')

    def _cleanup_stale_ports(self, state: Dict) -> None:
        """Clean up ports that are no longer in use.

        Args:
            state: Current state dictionary (modified in-place)
        """
        stale_ports = []

        for port_str, allocation in state['allocated_ports'].items():
            port = int(port_str)
            pid = allocation.get('pid')

            # Check if process is still alive
            process_alive = False
            if pid:
                try:
                    # Use execute to check if process exists (kill -0)
                    execute(
                        'kill', '-0', str(pid),
                        params=ExecuteParams(raise_on_error=True)
                    )
                    process_alive = True
                except (ExecuteError, OSError):
                    pass

            # Check if port is actually in use
            port_in_use = not self._is_port_actually_free(port)

            # If process is dead and port is free, mark as stale
            if not process_alive and not port_in_use:
                stale_ports.append(port)

        # Release stale ports
        for port in stale_ports:
            port_str = str(port)
            vm_id = state['allocated_ports'][port_str]['vm_id']
            LOG.info(f'Cleaning up stale port {port} from VM {vm_id}')
            del state['allocated_ports'][port_str]
            if port not in state['free_ports']:
                state['free_ports'].append(port)

        if stale_ports:
            state['free_ports'].sort()
            state['last_cleanup'] = datetime.now(timezone.utc).isoformat()
            LOG.info(f'Cleaned up {len(stale_ports)} stale ports')

    def cleanup_stale_ports(self) -> int:
        """Public interface for cleaning up stale ports.

        Returns:
            int: Number of ports cleaned up
        """
        with self._acquire_lock():
            state = self._load_state()
            initial_count = len(state['allocated_ports'])
            self._cleanup_stale_ports(state)
            self._save_state(state)
            cleaned_count = initial_count - len(state['allocated_ports'])
            return cleaned_count

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
                'last_cleanup': state.get('last_cleanup'),
                'port_range': f'{VNC_WS_PORT_START}-{VNC_WS_PORT_END}',
            }
