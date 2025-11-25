"""Libvirt connection management.

This module provides a context manager for handling connections to the Libvirt
hypervisor, making it easier to open and close connections within a managed
context.

Classes:
    LibvirtConnection: Context manager for Libvirt connections.
"""

from typing import Any

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

    def __init__(self) -> None:
        """Initialize the LibvirtConnection instance."""
        self.connection = None

    def __enter__(self) -> libvirt.virConnect:  # type: ignore
        """Open a connection to the Libvirt hypervisor.

        Returns:
            libvirt.virConnect: The active Libvirt connection.
        """
        self.connection = libvirt.open('qemu:///system')
        return self.connection

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Close the connection to the Libvirt hypervisor."""
        if self.connection is not None:
            self.connection.close()
