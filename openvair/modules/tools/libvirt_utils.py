"""Libvirt connection management.

This module provides a context manager for handling connections to the Libvirt
hypervisor, making it easier to open and close connections within a managed
context.

Classes:
    LibvirtConnection: Context manager for Libvirt connections.
"""

import libvirt

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


class LibvirtConnection:
    """Context manager for Libvirt connections.

    This class provides a context manager to handle the opening and closing
    of a connection to the Libvirt hypervisor.

    Attributes:
        connection: The active Libvirt connection instance.
    """

    def __init__(self):
        """Initialize the LibvirtConnection instance."""
        self.connection = None

    def __enter__(self):
        """Open a connection to the Libvirt hypervisor.

        Returns:
            libvirt.virConnect: The active Libvirt connection.
        """
        self.connection = libvirt.open('qemu:///system')
        return self.connection

    def __exit__(self, *args):
        """Close the connection to the Libvirt hypervisor."""
        if self.connection is not None:
            self.connection.close()
