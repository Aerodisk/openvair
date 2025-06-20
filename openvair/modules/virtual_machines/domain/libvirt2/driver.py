"""Module for Libvirt-based virtual machine management.

This module provides a `LibvirtDriver` class for managing virtual machines
using the Libvirt API. It includes methods for starting, stopping, and
managing VNC sessions for virtual machines.

Classes:
    LibvirtDriver: A driver for managing virtual machines using the
        Libvirt API.
"""

from typing import Any, Dict, List
from pathlib import Path

import libvirt

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.virtual_machines.config import (
    SERVER_IP,
    SNAPSHOTS_PATH,
)
from openvair.modules.virtual_machines.domain.base import BaseLibvirtDriver
from openvair.modules.virtual_machines.domain.exceptions import (
    SnapshotError,
    VNCSessionError,
    SnapshotXmlError,
)

LOG = get_logger(__name__)


class LibvirtDriver(BaseLibvirtDriver):
    """Driver class for managing virtual machines using the Libvirt API.

    This class provides methods to start, stop, manage VNC sessions and
    snapshots for virtual machines.

    Attributes:
        vm_info (Dict): Dictionary containing the virtual machine configuration.
        snapshot_info (Dict): Dictionary containing the snapshot configuration.
        vm_xml (str): The XML definition of the virtual machine.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a new instance of the LibvirtDriver class.

        Args:
            **kwargs: A dictionary containing the virtual machine
                configuration.
        """
        super(LibvirtDriver, self).__init__()
        self.snapshot_info = kwargs.pop('snapshot_info', None)
        self.vm_info = kwargs
        self.vm_xml = self.render_domain(self.vm_info)

    def start(self) -> Dict:
        """Start the virtual machine.

        This method creates a virtual machine using the Libvirt API and
        retrieves its power state, graphic URL, and graphic port.

        Returns:
            Dict: A dictionary containing the power state, URL, and
            port of the virtual machine.

        Raises:
            Exception: If an error occurs while starting the virtual machine.
        """
        LOG.info(f'Starting VM {self.vm_info.get("name")}')
        with self.connection as connection:
            domain = connection.createXML(self.vm_xml)
            state, _ = domain.state()
            domain_xml = domain.XMLDesc()
            graphic_port = self._get_graphic_port_from_xml(domain_xml)
            graphic_url = self._get_graphic_url(domain_xml)

            LOG.info(f'Generated graphic_url: {graphic_url}')
            LOG.info(f'Generated graphic_port: {graphic_port}')

            # Save the graphic interface information
            self.vm_info['graphic_interface'] = {
                'url': f'{graphic_url}:{graphic_port}' if graphic_url else '',
            }

        return {'power_state': state, 'url': graphic_url, 'port': graphic_port}

    def turn_off(self) -> Dict:
        """Turn off the virtual machine.

        This method stops the virtual machine using the Libvirt API.

        Returns:
            Dict: An empty dictionary representing the result of the operation.

        Raises:
            Exception: If an error occurs while turning off the
            virtual machine.
        """
        LOG.info(f'Turning off VM {self.vm_info.get("name")}')
        with self.connection as connection:
            domain = connection.lookupByName(self.vm_info.get('name'))
            domain.destroy()
        return {}

    def vnc(self) -> Dict:
        """Start a VNC session for the virtual machine.

        This method starts a VNC session using the `websockify` tool and
        returns the URL for accessing the VNC session.

        Returns:
            Dict: A dictionary containing the URL of the VNC session.

        Raises:
            ValueError: If the graphic interface URL is not set or is invalid.
            RuntimeError: If starting `websockify` fails.
        """
        LOG.info(f'Starting VNC for VM {self.vm_info.get("name")}')

        graphic_interface = self.vm_info.get('graphic_interface', {})
        LOG.info(f'Graphic interface info: {graphic_interface}')

        vm_url = graphic_interface.get('url')

        if not vm_url:
            LOG.error(
                f'Graphic interface URL not set for VM '
                f'{self.vm_info.get("name")}'
            )
            msg = 'Graphic interface URL is not set'
            raise ValueError(msg)

        try:
            port = vm_url.split(':')[-1]
            vnc_port = f'6{port[1:]}'
        except (AttributeError, IndexError) as err:
            LOG.error(f'Invalid graphic interface URL format: {vm_url}')
            msg = f'Invalid graphic interface URL format: {vm_url}'
            raise ValueError(msg) from err

        try:
            execute(
                'websockify',
                '-D',
                '--run-once',
                '--web',
                '/opt/aero/openvair/openvair/libs/noVNC/',
                vnc_port,
                f'localhost:{port}',
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    shell=True,
                    raise_on_error=True
                ),
            )
        except (ExecuteError, OSError) as err:
            msg = f'Failed to start websockify: {err!s}'
            LOG.error(msg)
            raise VNCSessionError(msg)

        vnc_url = (
            f'http://{SERVER_IP}:{vnc_port}/vnc.html?'
            f'host={SERVER_IP}&port={vnc_port}'
        )
        return {'url': vnc_url}

    def create_internal_snapshot(self) -> None:
        """Create an internal snapshot of the virtual machine.

        Method creates a snapshot of the virtual machine using the Libvirt API.

        Raises:
            Exception: If an error occurs while creating the snapshot.
        """
        LOG.info(f'Creating snapshot for VM {self.vm_info.get("name")}')

        vm_name = self.vm_info.get('name')
        name = self.snapshot_info.get('snapshot_name')
        description = self.snapshot_info.get('description')
        description = 'Open vAIR' if description is None else description

        with self.connection as connection:
            domain = connection.lookupByName(vm_name)

            snapshot_xml = f"""
            <domainsnapshot>
                <name>{name}</name>
                <description>{description}</description>
            </domainsnapshot>
            """

            try:
                snapshot = domain.snapshotCreateXML(snapshot_xml, flags=0)

                if not snapshot:
                    message = (f"Failed to create snapshot {name} "
                               f"for VM {vm_name}")
                    raise SnapshotError(message)
                snap_xml_desc = snapshot.getXMLDesc()
                snapshot_file = Path(f"{SNAPSHOTS_PATH}{vm_name}_{name}.xml")

                try:
                    snapshot_file.parent.mkdir(parents=True, exist_ok=True)
                    with snapshot_file.open('w', encoding='utf-8') as f:
                        f.write(snap_xml_desc)
                    LOG.debug(f"Saved snapshot XML to {snapshot_file}")
                except (IOError, OSError) as e:
                    message = f"Failed to save snapshot XML: {e}"
                    raise SnapshotError(message)

                LOG.info(f'Successfully created snapshot {name} '
                         f'for VM {vm_name}')

            except libvirt.libvirtError as e:
                message = (f"Libvirt error while creating snapshot {name} "
                           f"for VM {vm_name}: {e}")
                LOG.error(message)
                raise SnapshotError(message)

    def revert_internal_snapshot(self) -> None:
        """Revert the virtual machine to an internal snapshot.

        Method reverts a snapshot of the virtual machine using the Libvirt API.

        Raises:
            Exception: If an error occurs while reverting the snapshot.
        """
        LOG.info(f'Reverting snapshot for VM {self.vm_info.get("name")}')

        vm_name = self.vm_info.get('name')
        name = self.snapshot_info.get('snapshot_name')

        with self.connection as connection:
            domain = connection.lookupByName(vm_name)
            snapshot = domain.snapshotLookupByName(name)

            try:
                domain.revertToSnapshot(snapshot)
                LOG.info(f'Successfully reverted VM {vm_name} to the '
                         f'snapshot {name}')
            except libvirt.libvirtError as e:
                message = (f"Libvirt error while reverting VM {vm_name} to the "
                           f"snapshot {name}: {e}")
                LOG.error(message)
                raise SnapshotError(message)

    def delete_internal_snapshot(self) -> None:
        """Delete an internal snapshot of the virtual machine.

        Deletes a snapshot of the virtual machine using the Libvirt API or QEMU
        command (in case of shut-off VM) and updates XML files.

        Raises:
            SnapshotError: If an error occurs while deleting the snapshot.
            SnapshotXmlError: If there are issues processing snapshot XML.
        """
        vm_name = self.vm_info.get('name')
        snapshot_name = self.snapshot_info.get('snapshot_name')
        if not vm_name or not snapshot_name:
            message = "VM name or snapshot name is missing or invalid"
            raise SnapshotError(message)

        LOG.info(f'Deleting snapshot for VM {vm_name}')

        try:
            child_names = self._get_snapshot_child_names(vm_name, snapshot_name)
            if self._is_vm_running(vm_name):
                self._delete_with_libvirt(vm_name, snapshot_name)
            else:
                self._delete_with_qemu(vm_name, snapshot_name)
            self._process_snapshot_xml(vm_name, snapshot_name, child_names)
        except SnapshotError as e:
            message = f"Failed to delete snapshot: {e}"
            raise SnapshotError(message)
        else:
            self._cleanup_snapshot_files(vm_name, snapshot_name)
            LOG.info(f'Successfully deleted snapshot {snapshot_name} '
                     f'for VM {vm_name}')

    def _get_snapshot_child_names(
            self,
            vm_name: str,
            snapshot_name: str
    ) -> List[str]:
        """Find child snapshots in XML files.

        Args:
            vm_name (str): Name of the virtual machine
            snapshot_name (str): Name of the parent snapshot

        Returns:
            List[str]: Names of child snapshots referencing the given parent

        Raises:
            SnapshotError: If unable to read snapshot directory
        """
        child_names = []
        try:
            for child_file in Path(SNAPSHOTS_PATH).glob(f"{vm_name}_*.xml"):
                try:
                    with child_file.open('r', encoding='utf-8') as f:
                        child_xml = f.read()
                    child_parent = self._get_snapshot_parent_from_xml(child_xml)
                    if child_parent == snapshot_name:
                        child_name = child_file.stem.split('_')[-1]
                        child_names.append(child_name)
                except (OSError, SnapshotXmlError) as e:
                    message = f"Skipping snapshot file {child_file.name}: {e}"
                    LOG.warning(message)
                    continue
        except OSError as e:
            message = "Failed to scan snapshot files directory"
            LOG.error(message)
            raise SnapshotError(message) from e

        return child_names

    def _process_snapshot_xml(
            self,
            vm_name: str,
            snapshot_name: str,
            child_names: List[str]
    ) -> None:
        """Update XML references for child snapshots after parent deletion.

        Args:
            vm_name (str): Name of the virtual machine
            snapshot_name (str): Name of the deleted snapshot
            child_names (List): List of child snapshots names

        Raises:
            SnapshotError: If XML processing fails
        """
        snapshot_file = Path(f"{SNAPSHOTS_PATH}{vm_name}_{snapshot_name}.xml")

        try:
            with snapshot_file.open('r', encoding='utf-8') as f:
                snap_xml = f.read()
            parent_name = self._get_snapshot_parent_from_xml(snap_xml)
        except (IOError, OSError, SnapshotXmlError) as e:
            message = f"Failed to read snapshot XML file: {e}"
            LOG.error(message)
            raise SnapshotError(message)

        for child_name in child_names:
            child_file = Path(f"{SNAPSHOTS_PATH}{vm_name}_{child_name}.xml")

            try:
                with child_file.open('r', encoding='utf-8') as f:
                    child_xml = f.read()
                updated_xml = self._update_child_xml(child_xml, parent_name)
                with child_file.open('w', encoding='utf-8') as f:
                    f.write(updated_xml)
                LOG.debug(f"Updated parent reference in {child_file}")
            except (IOError, OSError, SnapshotXmlError) as e:
                message = f"Failed to update child snapshot {child_name}: {e}"
                LOG.error(message)
                raise SnapshotError(message)

    @staticmethod
    def _cleanup_snapshot_files(vm_name: str, snapshot_name: str) -> None:
        """"Remove snapshot XML files after successful deletion.

        Args:
            vm_name (str): Name of the virtual machine
            snapshot_name (str): Name of the deleted snapshot
        """
        snapshot_file = Path(f"{SNAPSHOTS_PATH}{vm_name}_{snapshot_name}.xml")

        try:
            if snapshot_file.exists():
                snapshot_file.unlink()
                LOG.debug(f"Deleted snapshot XML file {snapshot_file}")
        except (IOError, OSError) as e:
            LOG.warning(f"Failed to delete snapshot XML file: {e}")

    def _delete_with_libvirt(self, vm_name: str, snap_name: str) -> None:
        """Delete snapshot using libvirt API for running VMs.

        Args:
            vm_name (str): Name of the virtual machine
            snap_name (str): Name of the snapshot to delete

        Raises:
            SnapshotError: If libvirt operations fail during deletion
        """
        with self.connection as conn:
            try:
                domain = conn.lookupByName(vm_name)
                snapshot = domain.snapshotLookupByName(snap_name)
                snapshot.delete(flags=0)
            except libvirt.libvirtError as e:
                message = (f"Libvirt error while deleting snapshot "
                           f"{snap_name} for VM {vm_name}: {e}")
                LOG.error(message)
                raise SnapshotError(message)

    def _delete_with_qemu(self, vm_name: str, snap_name: str) -> None:
        """Delete snapshot using qemu-img command for shut-offed VMs.

        Args:
            vm_name (str): Name of the virtual machine
            snap_name (str): Name of the snapshot to delete

        Raises:
            SnapshotError: If qemu-img command fails or disk path is invalid
        """
        try:
            snap_file = Path(f"{SNAPSHOTS_PATH}{vm_name}_{snap_name}.xml")
            with snap_file.open('r', encoding='utf-8') as f:
                snap_xml = f.read()
            disk_path = self._get_snap_disk_path_from_xml(snap_xml)
            execute(
                'qemu-img',
                'snapshot',
                '-d',
                snap_name,
                disk_path,
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    run_as_root=True,
                    raise_on_error=True
                )
            )
        except SnapshotError as e:
            message = f"qemu-img snapshot deletion failed: {e}"
            raise SnapshotError(message)

    def _is_vm_running(self, vm_name: str) -> bool:
        """Check virtual machine running state via libvirt API.

        Args:
            vm_name (str): Name of the virtual machine to check

        Returns:
            bool: True if VM is currently active, False otherwise
        """
        try:
            with self.connection as conn:
                domain = conn.lookupByName(vm_name)
                return bool(domain.isActive())
        except libvirt.libvirtError:
            return False
