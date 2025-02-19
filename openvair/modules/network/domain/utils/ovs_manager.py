"""Open vSwitch (OVS) bridge and interface management.

This module provides a class for managing Open vSwitch (OVS) bridges and
interfaces, including methods for creating and deleting bridges, adding and
removing interfaces, configuring IP addresses, and checking bridge and
interface existence.

Classes:
    OVSManager: A class for managing Open vSwitch (OVS) bridges and
        interfaces.
"""

import json
from typing import Dict, List, Optional

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.modules.network.domain.utils.exceptions import (
    OVSManagerException,
    BridgeNotFoundException,
    InterfaceNotFoundException,
)

LOG = get_logger(__name__)


class OVSManager:
    """A class for managing Open vSwitch (OVS) bridges and interfaces.

    This class provides methods for creating and deleting OVS bridges,
    adding and removing interfaces from bridges, configuring IP addresses
    for interfaces, and modifying interface options.

    Attributes:
        command_format (str): Base command for OVS management.
        bridge_prefix (str): Prefix for bridge names.
    """

    def __init__(self) -> None:
        """Initialize OVSManager with command configurations.

        Args:
            sudo_required (bool): Flag to run commands with sudo.
            command_format (str): Base command for OVS management.
            bridge_prefix (str): Prefix for bridge names.
        """
        self.command_format = 'ovs-vsctl'

    def _build_command(self, subcommand: str) -> str:
        """Constructs a command with the configured settings.

        Args:
            subcommand (str): Subcommand to append to the base command.

        Returns:
            str: Full command string to execute.
        """
        command = f'{self.command_format} {subcommand}'
        LOG.debug(f'Constructed command: {command}')
        return command

    def create_bridge(self, bridge_name: Optional[str] = None) -> str:
        """Create a new OVS bridge with optional custom name.

        Args:
            bridge_name (Optional[str]): Name of the bridge.

        Returns:
            str: Command execution output.

        Raises:
            OVSManagerException: If bridge creation fails.
        """
        command = self._build_command(f'add-br {bridge_name}')
        LOG.info(f'Creating bridge: {bridge_name}')
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = f'Error creating bridge {bridge_name}: {exec_res.stderr}'
            LOG.error(message)
            raise OVSManagerException(message)
        return exec_res.stdout.strip()

    def delete_bridge(self, bridge_name: str) -> None:
        """Delete an OVS bridge with the specified name.

        Args:
            bridge_name (str): Name of the bridge to delete.

        Raises:
            BridgeNotFoundException: If the bridge is not found or cannot be
                deleted.
        """
        command = self._build_command(f'del-br {bridge_name}')
        LOG.info(f'Deleting bridge: {bridge_name}')
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            messsage = (
                f'Bridge {bridge_name} not found or could not be deleted: '
                '{stderr}'
            )
            LOG.error(messsage)
            raise BridgeNotFoundException(messsage)

    def add_interface(
        self, bridge_name: str, iface_name: str, tag: Optional[int] = None
    ) -> str:
        """Add an interface to an OVS bridge with an optional VLAN tag.

        Args:
            bridge_name (str): The name of the OVS bridge.
            iface_name (str): The name of the interface to add.
            tag (Optional[int]): VLAN tag for the interface.

        Returns:
            str: Command execution output.

        Raises:
            InterfaceNotFoundException: If adding the interface fails.
        """
        command = self._build_command(f'add-port {bridge_name} {iface_name}')
        if tag is not None:
            command += f' tag={tag} -- set interface {iface_name} type=internal'
        LOG.info(
            f'Adding interface {iface_name} to bridge '
            f'{bridge_name} with tag {tag}'
        )
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = (
                f'Error adding interface {iface_name} to bridge {bridge_name}: '
                f'{exec_res.stderr}'
            )
            LOG.error(message)
            raise InterfaceNotFoundException(message)
        return exec_res.stdout.strip()

    def get_ports_in_bridge(self, bridge_name: str) -> List:
        """Retrieve a list of ports within a specified OVS bridge.

        Args:
            bridge_name (str): The name of the OVS bridge from which to list
                ports.

        Returns:
            List[str]: A list of port names in the specified bridge.

        Raises:
            OVSManagerException: If an error occurs while retrieving the ports.
        """
        command = self._build_command(f'list-ports {bridge_name}')
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = f'Error while getting port in bridge: {bridge_name}'
            LOG.error(message)
            raise OVSManagerException(message)
        return exec_res.stdout.split()

    def get_bridges(self) -> Dict:
        """Retrieve all OVS bridges in JSON format.

        Returns:
            Dict: JSON object containing OVS bridges.

        Raises:
            OVSManagerException: If retrieving bridges fails.
        """
        command = self._build_command('--format=json list bridge')
        LOG.info('Retrieving list of bridges')
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = f'Error retrieving bridge list: {exec_res.stderr}'
            LOG.error(message)
            raise OVSManagerException(message)
        bridges: Dict = json.loads(exec_res.stdout)
        return bridges
