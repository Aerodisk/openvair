"""Module for interacting with libvirt domains.

This module provides functionality for managing and retrieving information
about virtual machine domains using the libvirt API. It establishes a
connection to the libvirt service and offers utilities for querying the state
of virtual machines.

Attributes:
    CONNECTION (LibvirtConnection): A global instance of the LibvirtConnection
        class used to manage the connection to the libvirt service.

Functions:
    get_vms_state(): Retrieves the current state of all virtual machine domains.
"""

from typing import Dict

import libvirt

from openvair.libs.libvirt.connection import LibvirtConnection

CONNECTION = LibvirtConnection()


def get_vms_state() -> Dict[str, str]:
    """Retrieve the state of all virtual machines.

    This function connects to the libvirt service and retrieves the current
    state of all available virtual machines. It returns a dictionary where
    the keys are VM names and the values are their states ('running' or
    'stopped').

    Returns:
        Dict[str, str]: A dictionary mapping VM names to their current state.
    """
    with CONNECTION as conn:
        vms = {}
        for domain in conn.listAllDomains():
            state, _ = domain.state()
            vms[domain.name()] = (
                'running' if state == libvirt.VIR_DOMAIN_RUNNING else 'stopped'
            )
    return vms
