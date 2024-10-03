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
import subprocess
from typing import Dict, List, Optional

from openvair.libs.log import get_logger
from openvair.modules.network.domain.bridges.utils.exceptions import (
    OVSManagerException,
    BridgeNotFoundException,
    InterfaceNotFoundException,
)
from openvair.modules.network.domain.bridges.utils.ip_manager import (
    NetworkIPManager,
)

LOG = get_logger(__name__)


class OVSManager:
    """A class for managing Open vSwitch (OVS) bridges and interfaces.

    This class provides methods for creating and deleting OVS bridges,
    adding and removing interfaces from bridges, configuring IP addresses
    for interfaces, and modifying interface options.

    Attributes:
        network_manager (NetworkIPManager): An instance of NetworkIPManager
            to handle network interface operations.
    """

    def __init__(self):
        """Initialize OVSManager.

        This constructor initializes the network manager used to perform
        network interface operations.
        """
        self.network_manager = NetworkIPManager()

    @staticmethod
    def _execute_command(command: str) -> subprocess.CompletedProcess:
        """Execute a shell command.

        Args:
            command (str): The shell command to execute.

        Returns:
            subprocess.CompletedProcess: The result of the command execution.
        """
        return subprocess.run(  # noqa: S602
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def create_bridge(self, bridge_name: str) -> str:
        """Create a new OVS bridge.

        Args:
            bridge_name (str): The name of the new bridge.

        Returns:
            str: The output of the command.

        Raises:
            OVSManagerException: If the bridge creation fails.
        """
        command = f'sudo ovs-vsctl add-br {bridge_name}'
        result = self._execute_command(command)
        if result.returncode != 0:
            msg = f'Error creating bridge {bridge_name}: {result.stderr}'
            raise OVSManagerException(msg)
        return result.stdout.strip()

    def create_configuration(self, data: Dict) -> None:
        """Create an OVS bridge and configure its interfaces.

        This method takes a dictionary 'data' containing information about the
        bridge and its interfaces. It creates the OVS bridge, configures custom
        IP addresses, adds specified ports to the bridge, turns the bridge on,
        and replaces the IP from the main interface on the bridge if it was
        included.

        Args:
            data (Dict): A dictionary containing information about the OVS
                bridge and interfaces.

        Raises:
            OVSManagerException: If any step of the configuration process fails.
        """
        interface_name = data.get('name')

        # Turn the bridge on
        self.network_manager.turn_on_interface(interface_name)

        # Add custom IP address if it was specified
        custom_ip = data.get('ip')
        if custom_ip:
            self.network_manager.set_interface_address(
                interface_name, custom_ip
            )

        # configure the bridge interfaces if they were specified
        if data.get('interfaces'):
            port_names = [
                port.get('name') for port in data.get('interfaces', [])
            ]

            # Add ports into the bridge
            self.add_ports(interface_name, port_names)

            # Replace IP from main interface on the bridge if it was included
            main_port_name = self.network_manager.get_main_port_name()
            if main_port_name in port_names:
                self.network_manager.run_dhclient(main_port_name)
                self._configure_main_port(interface_name, main_port_name)

    def delete_configuration(
        self,
        interface_name: Optional[str] = None,  # noqa: ARG002 need global domain refactoring including this problem
    ) -> None:
        """Delete the configuration of an OVS bridge and release resources.

        This method deletes the OVS bridge configuration for the specified
        interface and releases associated resources, such as running DHCP
        client and flushing IP addresses.

        Args:
            interface_name (Optional[str]): The name of the OVS bridge
                interface to delete.

        Raises:
            OVSManagerException: If any step of the deletion process fails.
        """
        main_port_name = self.network_manager.get_main_port_name()

        if not self.network_manager.get_interface_ip_address(main_port_name):
            self.network_manager.run_dhclient(main_port_name)

    def delete_bridge(self, bridge_name: str) -> str:
        """Delete an OVS bridge.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            str: The output of the command.

        Raises:
            BridgeNotFoundException: If the bridge is not found.
        """
        command = f'sudo ovs-vsctl del-br {bridge_name}'
        result = self._execute_command(command)
        if result.returncode != 0:
            msg = (
                f'Bridge {bridge_name} not found or could not be deleted: '
                f'{result.stderr}'
            )
            raise BridgeNotFoundException(msg)
        return result.stdout.strip()

    def add_interface(
        self, bridge_name: str, interface_name: str, tag: Optional[int] = None
    ) -> str:
        """Add an interface to an OVS bridge.

        Args:
            bridge_name (str): The name of the OVS bridge.
            interface_name (str): The name of the interface to add.
            tag (Optional[int]): VLAN tag for the interface (optional).

        Returns:
            str: The output of the command.

        Raises:
            InterfaceNotFoundException: If the interface addition fails.
        """
        # First, add the interface to the bridge
        command = f'sudo ovs-vsctl add-port {bridge_name} {interface_name}'

        # If a VLAN tag is specified, add it to the command
        if tag is not None:
            command += f' tag={tag}'

        # Set the interface type to internal
        command += f' -- set interface {interface_name} type=internal'

        result = self._execute_command(command)
        if result.returncode != 0:
            msg = (
                f'Error adding interface {interface_name} to bridge '
                f'{bridge_name}: {result.stderr}'
            )
            raise InterfaceNotFoundException(msg)
        return result.stdout.strip()

    def remove_interface(self, bridge_name: str, interface_name: str) -> str:
        """Remove an interface from an OVS bridge.

        Args:
            bridge_name (str): The name of the OVS bridge.
            interface_name (str): The name of the interface to remove.

        Returns:
            str: The output of the command.

        Raises:
            InterfaceNotFoundException: If the interface removal fails.
        """
        command = f'sudo ovs-vsctl del-port {bridge_name} {interface_name}'
        result = self._execute_command(command)
        if result.returncode != 0:
            msg = (
                f'Error removing interface {interface_name} '
                f'from bridge {bridge_name}: {result.stderr}'
            )
            raise InterfaceNotFoundException(msg)
        return result.stdout.strip()

    def edit_interface_address(
        self,
        interface_name: str,
        old_ip_address: str,
        new_ip_address: str,
    ) -> str:
        """Edit the IP address for an OVS interface.

        Remove old IP address and set a new IP address.

        Args:
            interface_name (str): The name of the OVS interface.
            old_ip_address (str): The old IP address.
            new_ip_address (str): The new IP address.

        Returns:
            str: The output of the command.

        Raises:
            InvalidAddressException: If editing the IP address fails.
        """
        self.network_manager.remove_interface_address(
            interface_name, old_ip_address
        )
        return self.network_manager.set_interface_address(
            interface_name, new_ip_address
        )

    def edit_interface(self, interface_name: str, options: str) -> str:
        """Edit the configuration options for an OVS interface.

        Args:
            interface_name (str): The name of the OVS interface.
            options (str): The new configuration options.

        Returns:
            str: The output of the command.

        Raises:
            OVSManagerException: If editing the interface fails.
        """
        command = f'sudo ovs-vsctl set Interface {interface_name} {options}'
        result = self._execute_command(command)
        if result.returncode != 0:
            msg = f'Error editing interface {interface_name}: {result.stderr}'
            raise OVSManagerException(msg)
        return result.stdout.strip()

    def check_bridge_existence(self, bridge_name: str) -> bool:
        """Check if an OVS bridge exists.

        Args:
            bridge_name (str): The name of the OVS bridge.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        command = f'sudo ovs-vsctl br-exists {bridge_name}'
        result = self._execute_command(command)
        return result.returncode == 0

    def check_interface_existence(
        self, bridge_name: str, interface_name: str
    ) -> bool:
        """Check if an OVS interface exists in a specific bridge.

        Args:
            bridge_name (str): The name of the OVS bridge.
            interface_name (str): The name of the OVS interface.

        Returns:
            bool: True if the interface exists in the bridge, False otherwise.
        """
        command = f'sudo ovs-vsctl list-ports {bridge_name}'
        result = self._execute_command(command)
        return interface_name in result.stdout.strip().splitlines()

    def add_ports(self, interface_name: str, ports_list: List) -> None:
        """Add a list of ports to the OVS bridge.

        Args:
            interface_name (str): The name of the bridge.
            ports_list (List): List of port names as strings.

        Raises:
            OVSManagerException: If adding any of the ports fails.
        """
        LOG.info('Start adding ports into the bridge')
        for port_name in ports_list:
            command = f'sudo ovs-vsctl add-port {interface_name} {port_name}'
            result = self._execute_command(command)

            if result.returncode != 0:
                msg = (
                    f"Failure while adding port '{port_name}':"
                    f' {result.stderr}'
                )
                raise OVSManagerException(msg)
        LOG.info('All ports were successfully added')

    def get_bridges_list(self) -> List:
        """Get the list of OVS bridges.

        Returns:
            List: A list of OVS bridge interfaces.

        Raises:
            OVSManagerException: If retrieving the list of bridges fails.
        """
        # Collect list of OVS bridges
        ovs_exec_result = self._execute_command(
            'sudo ovs-vsctl --format=json list bridge'
        )
        if ovs_exec_result.returncode != 0:
            msg = (
                f'Failure while removing IP from port: {ovs_exec_result.stderr}'
            )
            raise OVSManagerException(msg)

        # Collect list of all Linux interfaces
        linux_exec_result = self._execute_command('ip -j link show')
        if linux_exec_result.returncode != 0:
            stderr_msq = linux_exec_result.stderr
            msg = f'Failure while removing IP from port: {stderr_msq}'
            raise OVSManagerException(msg)

        # Convert results of commands into dict
        ovs_bridges_info = json.loads(ovs_exec_result.stdout)
        linux_interfaces_data = json.loads(linux_exec_result.stdout.strip())

        # Find index of OVS bridge name in bridge-info list
        name_index = ovs_bridges_info['headings'].index('name')

        # Collect all OVS bridge names from ovs_bridges_info["data"]
        ovs_bridges_names = [
            bridge[name_index] for bridge in ovs_bridges_info['data']
        ]

        # Collect OVS bridge info from Linux interfaces info
        return [
            iface
            for iface in linux_interfaces_data
            if iface['ifname'] in ovs_bridges_names
            or iface['ifname'] == 'virbr0'
        ]

    def _configure_main_port(
        self,
        interface_name: str,
        main_port_name: str,
    ) -> None:
        """Move the IP address from the main interface to the bridge interface.

        Retrieves the IP address of the main interface, sets it on the bridge
        interface, and configures the base gateway accordingly.

        Args:
            interface_name (str): The name of the OVS bridge.
            main_port_name (str): The name of the main interface.

        Raises:
            OVSManagerException: If the main port configuration fails.
        """
        try:
            LOG.info('The main port was added into the bridge')
            main_port_ip = self.network_manager.get_interface_ip_address(
                main_port_name
            )
            gateway_ip = self.network_manager.get_default_gateway_ip(
                main_port_ip
            )

            LOG.info(f'Flushing IP from main port: {main_port_name}')
            self.network_manager.flush_ip_from_interface(main_port_name)

            LOG.info(
                f'Setting IP: {main_port_ip} to the bridge: {interface_name}'
            )
            self.network_manager.set_interface_address(
                interface_name, main_port_ip
            )

            LOG.info(
                f'Setting default gateway: {gateway_ip} to the'
                f' bridge: {interface_name}'
            )
            self.network_manager.set_default_gateway(gateway_ip)

            LOG.info(
                'Successfully moved the IP address of the main port '
                'to the bridge.'
            )
        except Exception as error:
            LOG.error(f'Failed to configure the main port: {error}')
            msg = 'Failed to configure the main port'
            raise OVSManagerException(
                msg
            ) from error
