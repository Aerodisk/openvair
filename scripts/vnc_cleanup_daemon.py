#!/usr/bin/env python3
"""VNC cleanup daemon for Open vAIR.

This script periodically cleans up stale VNC ports and orphaned websockify
processes to maintain system health and prevent resource exhaustion.
"""

import sys
import time
import signal
from pathlib import Path

# Add openvair to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openvair.libs.log import get_logger
from openvair.modules.virtual_machines.vnc.session_coordinator import VncSessionCoordinator

LOG = get_logger(__name__)


class VncCleanupDaemon:
    """Daemon for periodic VNC resource cleanup."""
    
    def __init__(self, cleanup_interval: int = 60):
        """Initialize the cleanup daemon.
        
        Args:
            cleanup_interval: Seconds between cleanup runs (default: 60)
        """
        self.cleanup_interval = cleanup_interval
        self.coordinator = VncSessionCoordinator()
        self._running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        LOG.info(f"Received signal {signum}, shutting down gracefully")
        self._running = False
    
    def run(self) -> None:
        """Run the cleanup daemon."""
        LOG.info(f"Starting VNC cleanup daemon (interval: {self.cleanup_interval}s)")
        
        while self._running:
            try:
                # Perform cleanup
                stats = self.coordinator.cleanup_stale_resources()
                
                # Log cleanup results
                if stats['stale_ports_cleaned'] > 0 or stats['orphaned_processes_cleaned'] > 0:
                    LOG.info(f"Cleanup completed: {stats}")
                else:
                    LOG.debug("Cleanup completed: no stale resources found")
                
                # Get system status
                status = self.coordinator.get_system_status()
                if status['system_health'] == 'warning':
                    LOG.warning(f"VNC system health warning: {status}")
                
            except Exception as e:
                LOG.error(f"Error during cleanup: {e}")
            
            # Sleep until next cleanup cycle
            for _ in range(self.cleanup_interval):
                if not self._running:
                    break
                time.sleep(1)
        
        LOG.info("VNC cleanup daemon stopped")


def main() -> None:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VNC cleanup daemon for Open vAIR")
    parser.add_argument(
        '--interval', 
        type=int, 
        default=60,
        help='Cleanup interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--once', 
        action='store_true',
        help='Run cleanup once and exit'
    )
    
    args = parser.parse_args()
    
    if args.once:
        # Run cleanup once and exit
        LOG.info("Running one-time VNC cleanup")
        coordinator = VncSessionCoordinator()
        stats = coordinator.cleanup_stale_resources()
        status = coordinator.get_system_status()
        
        print(f"Cleanup completed: {stats}")
        print(f"System status: {status}")
        
    else:
        # Run as daemon
        daemon = VncCleanupDaemon(cleanup_interval=args.interval)
        try:
            daemon.run()
        except KeyboardInterrupt:
            LOG.info("Daemon interrupted by user")


if __name__ == '__main__':
    main()
