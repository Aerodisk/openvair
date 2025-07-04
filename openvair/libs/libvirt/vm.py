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
    get_vm_snapshots(): Retrieves all snapshots for a VM and its
    current snapshot name.
"""

from typing import Set, Dict, Tuple, Optional

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


def get_vm_snapshots(vm_name: str) -> Tuple[Set[str], Optional[str]]:
    """Get all snapshots for a VM and its current snapshot name.

    Args:
        vm_name: Name of the virtual machine to check.

    Returns:
        Tuple: (Set(str), Optional(str)) - tuple containing:
        - Set of all snapshot names
        - Name of current snapshot (None if no current snapshot)
    """
    with CONNECTION as conn:
        try:
            domain = conn.lookupByName(vm_name)
            snapshots = domain.listAllSnapshots()
            if not snapshots:
                return set(), None
            current_snap = domain.snapshotCurrent()
            current_name = current_snap.getName() if current_snap else None
            return {snap.getName() for snap in snapshots}, current_name
        except libvirt.libvirtError:
            return set(), None
