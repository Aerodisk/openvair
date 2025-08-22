"""WebSockify process manager for VNC sessions.

This module manages the lifecycle of websockify processes, including starting,
stopping, and monitoring websockify instances for VNC connections.
"""

import threading
from typing import Dict, Optional

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.virtual_machines.vnc.exceptions import (
    WebsockifyProcessError,
)

LOG = get_logger(__name__)


class WebsockifyProcessManager:
    """Manager for websockify process lifecycle.

    This class handles starting, stopping, and monitoring websockify processes
    for VNC sessions. It maintains a registry of active processes and provides
    cleanup functionality.

    Attributes:
        _instance: Singleton instance
        _lock: Thread lock for singleton initialization
        _processes: Registry of active websockify processes
        _process_lock: Lock for process registry operations
    """

    _instance: Optional['WebsockifyProcessManager'] = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls) -> 'WebsockifyProcessManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the process manager."""
        if not self._initialized:
            self._processes: Dict[str, Dict] = {}
            self._process_lock = threading.Lock()
            WebsockifyProcessManager._initialized = True
            LOG.info('WebSockify Process Manager initialized')

    def start_websockify(
        self, vm_id: str, vnc_host: str, vnc_port: int, ws_port: int
    ) -> int:
        """Start a websockify process for VNC access.

        This method starts a websockify daemon process that bridges WebSocket
        connections to VNC. It includes automatic detection of existing processes
        and process ID discovery via port lookup.

        Args:
            vm_id: Virtual machine identifier
            vnc_host: VNC server host (typically localhost)
            vnc_port: VNC server port (e.g., 5900)
            ws_port: WebSocket port for websockify

        Returns:
            int: Process ID of started websockify process

        Raises:
            WebsockifyProcessError: If process startup fails or PID cannot be found
        """
        LOG.info(
            f'Starting websockify for VM {vm_id}: {vnc_host}:{vnc_port} -> ws:{ws_port}'
        )

        with self._process_lock:
            # Check if process already exists for this VM
            if vm_id in self._processes:
                existing_pid = self._processes[vm_id]['pid']
                if self._is_process_alive(existing_pid):
                    LOG.warning(
                        f'WebSockify already running for VM {vm_id} (PID: {existing_pid})'
                    )
                    return existing_pid
                else:
                    # Clean up dead process entry
                    del self._processes[vm_id]

            try:
                # Start websockify process
                execute(
                    'websockify',
                    '-D',  # Daemon mode
                    '--run-once',  # Exit after one connection
                    '--web',
                    '/opt/aero/openvair/openvair/libs/noVNC/',
                    str(ws_port),
                    f'{vnc_host}:{vnc_port}',
                    params=ExecuteParams(
                        run_as_root=True, shell=True, raise_on_error=True
                    ),
                )

                # Extract PID from websockify output or find by port
                pid = self._find_websockify_pid(ws_port)
                if not pid:
                    msg = f'Failed to find websockify PID for port {ws_port}'
                    raise WebsockifyProcessError(msg)

                # Register the process
                self._processes[vm_id] = {
                    'pid': pid,
                    'ws_port': ws_port,
                    'vnc_host': vnc_host,
                    'vnc_port': vnc_port,
                    'started_at': None,  # Could add timestamp if needed
                }

                LOG.info(f'Started websockify for VM {vm_id} (PID: {pid})')
                return pid

            except (ExecuteError, OSError) as e:
                error_msg = f'Failed to start websockify for VM {vm_id}: {e}'
                LOG.error(error_msg)
                raise WebsockifyProcessError(error_msg)

    def _find_websockify_pid(self, ws_port: int) -> Optional[int]:
        """Find websockify PID by port.

        Args:
            ws_port: WebSocket port to search for

        Returns:
            Optional[int]: PID if found, None otherwise
        """
        try:
            # Use lsof to find process using the port
            result = execute(
                f'lsof -ti:{ws_port}',
                params=ExecuteParams(run_as_root=True, shell=True),
            )

            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                # Return the first PID found
                return int(pids[0])

        except (ExecuteError, OSError, ValueError):
            # Fallback: search process list
            try:
                result = execute(
                    f'pgrep -f "websockify.*{ws_port}"',
                    params=ExecuteParams(shell=True),
                )

                if result.stdout.strip():
                    return int(result.stdout.strip().split('\n')[0])

            except (ExecuteError, ValueError):
                pass

        return None

    def stop_websockify(self, vm_id: str) -> bool:
        """Stop websockify process for a VM.

        Args:
            vm_id: Virtual machine identifier

        Returns:
            bool: True if process was stopped, False if not found
        """
        with self._process_lock:
            if vm_id not in self._processes:
                LOG.warning(f'No websockify process found for VM {vm_id}')
                return False

            process_info = self._processes[vm_id]
            pid = process_info['pid']
            process_info['ws_port']

            LOG.info(f'Stopping websockify for VM {vm_id} (PID: {pid})')

            success = self._terminate_process(pid)

            # Clean up registry
            del self._processes[vm_id]

            if success:
                LOG.info(f'Stopped websockify for VM {vm_id}')
            else:
                LOG.warning(f'Failed to cleanly stop websockify for VM {vm_id}')

            return success

    def _terminate_process(self, pid: int) -> bool:
        """Terminate a process gracefully, then forcefully if needed.

        This method first attempts a graceful shutdown using SIGTERM,
        waits briefly, then uses SIGKILL if the process is still alive.
        This ensures reliable cleanup of websockify processes.

        Args:
            pid: Process ID to terminate

        Returns:
            bool: True if process was successfully terminated
        """
        try:
            # Check if process exists
            if not self._is_process_alive(pid):
                return True  # Already dead

            # Try SIGTERM first using execute
            execute(
                'kill',
                '-TERM',
                str(pid),
                params=ExecuteParams(raise_on_error=True),
            )

            # Give it a moment to exit gracefully
            import time

            time.sleep(2)

            # Check if it's still alive
            if self._is_process_alive(pid):
                LOG.warning(
                    f"Process {pid} didn't respond to SIGTERM, sending SIGKILL"
                )
                execute(
                    'kill',
                    '-KILL',
                    str(pid),
                    params=ExecuteParams(raise_on_error=True),
                )
                time.sleep(1)

            # Final check
            return not self._is_process_alive(pid)

        except (ExecuteError, OSError):
            # Process already dead or doesn't exist
            return True

    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is alive.

        Args:
            pid: Process ID to check

        Returns:
            bool: True if process is alive
        """
        try:
            # Use execute to check if process exists (kill -0)
            execute(
                'kill',
                '-0',
                str(pid),
                params=ExecuteParams(raise_on_error=True),
            )
            return True
        except (ExecuteError, OSError):
            return False

    def get_active_sessions(self) -> Dict[str, Dict]:
        """Get information about active websockify sessions.

        Returns:
            Dict: Active sessions keyed by VM ID
        """
        with self._process_lock:
            # Return copy of current processes
            return {
                vm_id: info.copy() for vm_id, info in self._processes.items()
            }

