"""Netplan configuration management.

This module provides classes and methods to manage Netplan configurations,
including creating, updating, and deleting network bridges and interfaces
in YAML configuration files.

Classes:
    NetplanManager: Manager for handling Netplan configurations.
"""

import subprocess
from typing import Dict, List

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import (
    execute,
    read_yaml_file,
    write_yaml_file,
)
from openvair.modules.network.config import NETPLAN_YAML_FILE
from openvair.modules.network.service_layer import exceptions
from openvair.modules.network.domain.bridges.utils.ip_manager import (
    NetworkIPManager,
)

LOG = get_logger(__name__)


class NetplanManager:
    """Manager for handling Netplan configurations.

    This class provides methods to manage Netplan configurations, such as
    creating, updating, and deleting network bridges and interfaces in YAML
    configuration files.

    Attributes:
        network_manager (NetworkIPManager): An instance of NetworkIPManager
            to handle network interface operations.
    """

    def __init__(self):
        """Initialize NetplanManager.

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

    def write_yaml_file(self, netplan_config: Dict) -> None:
        """Write the Netplan configuration to a YAML file.

        Args:
            netplan_config (Dict): The Netplan configuration data.
        """
        write_yaml_file(NETPLAN_YAML_FILE, netplan_config)

    @staticmethod
    def apply() -> None:
        """Apply the current Netplan configuration."""
        execute('netplan apply', run_as_root=True)

    def create_configuration(self, data: Dict) -> None:
        """Create and apply a Netplan configuration.

        This method creates a Netplan configuration for a new network bridge
        and applies it.

        Args:
            data (Dict): Data about the new network bridge.
        """
        interface_name = data.get('name')
        self.network_manager.turn_on_interface(interface_name)

        if data.get('interfaces'):
            yaml_data = self.create_yaml_config_file(data)
            yaml_data['network']['bridges'][interface_name].setdefault(
                'addresses', []
            )
            port_names = [
                port.get('name') for port in data.get('interfaces', [])
            ]
            main_port_name = self.network_manager.get_main_port_name()

            if main_port_name in port_names:
                main_port_ip = self.network_manager.get_interface_ip_address(
                    main_port_name
                )

                yaml_data['network']['bridges'][interface_name][
                    'addresses'
                ].append(f'{main_port_ip}/24')

            self.write_yaml_file(yaml_data)
            self.apply()

    def delete_configuration(self, interface_name: str) -> None:
        """Delete a network bridge configuration.

        Args:
            interface_name (str): The name of the bridge to delete.
        """
        LOG.info(
            f'Start deleting configuration for interface: {interface_name}'
        )
        netplan_config = self._get_netplan_config_file_data()
        bridge_exists_flag = self._ensure_bridge_exists(
            interface_name, netplan_config
        )
        if bridge_exists_flag:
            self._delete_bridge_from_config(interface_name, netplan_config)
            self._update_renderer('NetworkManager', netplan_config)
            self.write_yaml_file(netplan_config)
            self.apply()

        main_interface_name = self.network_manager.get_main_port_name()
        if not self.network_manager.get_interface_ip_address(
            main_interface_name
        ):
            self.network_manager.run_dhclient(main_interface_name)

    @staticmethod
    def _prepare_interfaces_data_for_yaml_config(data: Dict) -> Dict:
        """Prepare interfaces data for the YAML configuration.

        Args:
            data (Dict): Data about the new bridge.

        Returns:
            Dict: Prepared interfaces data for the YAML configuration.
        """
        interfaces_config = {}
        for iface in data.get('interfaces', []):
            interfaces_config[iface['name']] = {'dhcp4': 'no', 'dhcp6': 'no'}
        return interfaces_config

    @staticmethod
    def _get_netplan_config_file_data() -> Dict:
        """Read the Netplan configuration file.

        Returns:
            Dict: Data from the Netplan configuration file.
        """
        config_file_data = read_yaml_file(NETPLAN_YAML_FILE)
        LOG.info(f'Netplan config file data: {config_file_data}')
        return config_file_data

    @staticmethod
    def _check_if_bridge_name_is_vacant(
        bridge_name: str, netplan_config: Dict
    ) -> None:
        """Check if a bridge name is available.

        Args:
            bridge_name (str): The name of the new bridge.
            netplan_config (Dict): The current Netplan configuration.

        Raises:
            BridgeNameExistException: If the bridge name is already in use.
        """
        if netplan_config['network'].get('bridges', {}).get(bridge_name, {}):
            message = f'Network bridge with name {bridge_name} already exists'
            LOG.error(message)
            raise exceptions.BridgeNameExistException(message)

    def _add_network_bridge(self, netplan_config: Dict, data: Dict) -> None:
        """Add a new network bridge to the Netplan configuration.

        Args:
            netplan_config (Dict): The current Netplan configuration.
            data (Dict): Data about the new network bridge.
        """
        bridge_name = data['name']
        bridge_ip = data.get('ip')

        netplan_config.setdefault('network', {}).setdefault('ethernets', {})
        netplan_config.setdefault('network', {}).setdefault('bridges', {})

        interfaces_config = self._prepare_interfaces_data_for_yaml_config(data)
        netplan_config['network']['ethernets'].update(interfaces_config)

        netplan_config['network']['bridges'][bridge_name] = {
            'interfaces': [iface['name'] for iface in data['interfaces']],
            'dhcp4': 'yes',
            'dhcp6': 'yes',
            'parameters': {'stp': False, 'forward-delay': 0},
            'openvswitch': {
                'external-ids': {
                    'iface-id': bridge_name,
                },
                'other-config': {'mtu': 1500},
            },
        }

        if bridge_ip:
            netplan_config['network']['bridges'][bridge_name].update(
                {'addresses': [f'{bridge_ip}/24']}
            )

    def create_yaml_config_file(self, data: Dict) -> Dict:
        """Create a dictionary for the Netplan configuration file.

        Args:
            data (Dict): Data about the new bridge.

        Returns:
            Dict: Data for the Netplan configuration file.
        """
        bridge_name = data['name']
        netplan_config = self._get_netplan_config_file_data()
        self._check_if_bridge_name_is_vacant(bridge_name, netplan_config)
        self._update_renderer('networkd', netplan_config)
        self._add_network_bridge(netplan_config, data)

        return netplan_config

    @staticmethod
    def _ensure_bridge_exists(
        interface_name: str, netplan_config: Dict
    ) -> bool:
        """Ensure that a network bridge exists in the Netplan configuration.

        Args:
            interface_name (str): The name of the network bridge.
            netplan_config (Dict): The current Netplan configuration.

        Returns:
            bool: True if the network bridge exists, False otherwise.
        """
        LOG.info(
            f'Ensure network bridge ({interface_name}) exists in Netplan config'
            ' file'
        )
        if (
            not netplan_config['network']
            .get('bridges', {})
            .get(interface_name, '')
        ):
            message = f'Bridge with name {interface_name} does not exist'
            LOG.info(message)
            return False
        return True

    @staticmethod
    def _get_bridges_interfaces(netplan_config: Dict) -> List:
        """Get all interfaces used in network bridges.

        Args:
            netplan_config (Dict): The current Netplan configuration.

        Returns:
            List: A list of interface names used in network bridges.
        """
        interfaces_list = []
        for br_name in netplan_config['network']['bridges']:
            ifaces_names_list = netplan_config['network']['bridges'][
                br_name
            ].get('interfaces', [])
            interfaces_list.extend(ifaces_names_list)
        return list(set(interfaces_list))

    @staticmethod
    def _del_bridges_if_empty(netplan_config: Dict) -> None:
        """Delete the bridges section from the Netplan configuration if empty.

        Args:
            netplan_config (Dict): The current Netplan configuration.
        """
        LOG.info('Check if the bridge section is empty')
        if not netplan_config['network']['bridges']:
            LOG.info('The bridge section is empty')
            netplan_config['network'].pop('bridges')

    def _clear_ethernets(self, netplan_config: Dict) -> None:
        """Delete unused ethernet objects from the Netplan configuration.

        Args:
            netplan_config (Dict): The current Netplan configuration.
        """
        LOG.info('Start to clear ethernets from the Netplan config file')
        bridges_list = self._get_bridges_interfaces(netplan_config)
        ethernets_to_delete = []

        for iface_name in netplan_config['network']['ethernets']:
            if iface_name not in bridges_list:
                ethernets_to_delete.append(iface_name)

        for iface_name in ethernets_to_delete:
            netplan_config['network']['ethernets'].pop(iface_name)

    @staticmethod
    def _del_ethernets_if_empty(netplan_config: Dict) -> None:
        """Delete the ethernets section from the Netplan configuration if empty.

        Args:
            netplan_config (Dict): The current Netplan configuration.
        """
        LOG.info('Check if the ethernets section is empty')
        if not netplan_config['network']['ethernets']:
            LOG.info('The ethernets section is empty')
            netplan_config['network'].pop('ethernets')

    def _delete_bridge_from_config(
        self,
        bridge_name: str,
        netplan_config: Dict,
    ) -> None:
        """Delete a bridge from the Netplan configuration.

        Args:
            bridge_name (str): The name of the bridge to delete.
            netplan_config (Dict): The current Netplan configuration.
        """
        LOG.info(f'Deleting bridge: {bridge_name} from config file')
        netplan_config['network']['bridges'].pop(bridge_name)
        self._clear_ethernets(netplan_config)
        self._del_bridges_if_empty(netplan_config)
        self._del_ethernets_if_empty(netplan_config)
        LOG.info(f'The bridge {bridge_name} was successfully deleted')

    @staticmethod
    def _update_renderer(new_renderer: str, netplan_config: Dict) -> None:
        """Update the 'renderer' value in the Netplan configuration.

        Args:
            new_renderer (str): The new value for the 'renderer' field.
            netplan_config (Dict): The current Netplan configuration.
        """
        netplan_config['network']['renderer'] = new_renderer
