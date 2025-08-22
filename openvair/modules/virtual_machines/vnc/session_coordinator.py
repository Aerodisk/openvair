"""VNC session coordinator for atomic resource management.

This module provides high-level coordination between port allocation and
process management, ensuring atomic operations for VNC session lifecycle.
"""

from typing import Dict, Optional
from contextlib import contextmanager

from openvair.libs.log import get_logger
from openvair.modules.virtual_machines.config import SERVER_IP
from openvair.modules.virtual_machines.vnc.port_pool_manager import (
    VncPortPoolManager,
)
from openvair.modules.virtual_machines.vnc.process_manager import (
    WebsockifyProcessManager,
)
from openvair.modules.virtual_machines.vnc.exceptions import (
    VncSessionCoordinationError,
    VncPortPoolExhaustedException,
    WebsockifyProcessError,
)

LOG = get_logger(__name__)


class VncSessionCoordinator:
    """Coordinates VNC session resources (ports + processes).

    This class provides atomic operations for VNC session management,
    ensuring that port allocation and process startup/shutdown are
    coordinated properly.

    Attributes:
        port_manager: Port pool manager instance
        process_manager: Process manager instance
    """

    def __init__(self) -> None:
        """Initialize the session coordinator."""
        self.port_manager = VncPortPoolManager()
        self.process_manager = WebsockifyProcessManager()
        LOG.debug('VNC Session Coordinator initialized')

    def start_vnc_session(
        self, vm_id: str, vnc_host: str, vnc_port: int
    ) -> Dict[str, str]:
        """Start a complete VNC session with atomic resource allocation.

        This method atomically allocates a WebSocket port and starts
        a websockify process, ensuring cleanup on failure.

        Args:
            vm_id: Virtual machine identifier
            vnc_host: VNC server host (typically localhost)
            vnc_port: VNC server port (e.g., 5900)

        Returns:
            Dict containing 'url', 'ws_port', and 'pid'

        Raises:
            VncSessionCoordinationError: If session startup fails
            VncPortPoolExhaustedException: If no ports available
        """
        LOG.info(f'Starting VNC session for VM {vm_id}')

        allocated_port = None
        started_pid = None

        try:
            # Step 1: Allocate WebSocket port (without PID initially)
            allocated_port = self.port_manager.allocate_port(vm_id)
            LOG.debug(f'Allocated port {allocated_port} for VM {vm_id}')

            # Step 2: Start websockify process
            started_pid = self.process_manager.start_websockify(
                vm_id=vm_id,
                vnc_host=vnc_host,
                vnc_port=vnc_port,
                ws_port=allocated_port,
            )
            LOG.debug(f'Started websockify PID {started_pid} for VM {vm_id}')

            # Step 3: Update port allocation with PID
            self.port_manager.update_port_pid(allocated_port, started_pid)

            # Step 4: Generate VNC URL
            vnc_url = self._generate_vnc_url(allocated_port)

            result = {
                'url': vnc_url,
                'ws_port': str(allocated_port),
                'pid': str(started_pid),
            }

            LOG.info(
                f'Successfully started VNC session for VM {vm_id}: {vnc_url}'
            )
            return result

        except Exception as e:
            # Cleanup on failure
            error_msg = f'Failed to start VNC session for VM {vm_id}: {e}'
            LOG.error(error_msg)

            # Rollback operations
            if started_pid:
                try:
                    self.process_manager.stop_websockify(vm_id)
                    LOG.debug(f'Cleaned up websockify process {started_pid}')
                except Exception as cleanup_error:
                    LOG.warning(
                        f'Failed to cleanup websockify process: {cleanup_error}'
                    )

            if allocated_port:
                try:
                    self.port_manager.release_port(allocated_port, vm_id)
                    LOG.debug(f'Released port {allocated_port}')
                except Exception as cleanup_error:
                    LOG.warning(f'Failed to release port: {cleanup_error}')

            # Re-raise with coordination error
            if isinstance(e, VncPortPoolExhaustedException):
                raise  # Re-raise port exhaustion as-is
            else:
                raise VncSessionCoordinationError(error_msg) from e

    def stop_vnc_session(self, vm_id: str) -> bool:
        """Stop a VNC session and release all resources.

        Args:
            vm_id: Virtual machine identifier

        Returns:
            bool: True if session was stopped successfully
        """
        LOG.info(f'Stopping VNC session for VM {vm_id}')

        success = True

        # Get session info before stopping
        active_sessions = self.process_manager.get_active_sessions()
        session_info = active_sessions.get(vm_id)

        try:
            # Stop websockify process
            process_stopped = self.process_manager.stop_websockify(vm_id)
            if not process_stopped:
                LOG.warning(f'Failed to stop websockify process for VM {vm_id}')
                success = False

            # Release port if we have session info
            if session_info:
                ws_port = session_info['ws_port']
                self.port_manager.release_port(ws_port, vm_id)
                LOG.debug(f'Released port {ws_port} for VM {vm_id}')

        except Exception as e:
            LOG.error(f'Error stopping VNC session for VM {vm_id}: {e}')
            success = False

        if success:
            LOG.info(f'Successfully stopped VNC session for VM {vm_id}')

        return success

    def _generate_vnc_url(self, ws_port: int) -> str:
        """Generate VNC URL for WebSocket port.

        Args:
            ws_port: WebSocket port number

        Returns:
            str: Complete VNC URL
        """
        return (
            f'http://{SERVER_IP}:{ws_port}/vnc.html?'
            f'host={SERVER_IP}&port={ws_port}'
        )

