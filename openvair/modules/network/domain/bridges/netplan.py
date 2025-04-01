"""Netplan-based network bridge management.

This module provides an implementation of the network bridge interface using
Netplan for managing network configurations.

Classes:
    NetplanInterface: Netplan-based implementation of the network bridge
        interface.
"""

from typing import Any, Dict
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.modules.network.domain.base import BaseOVSBridge
from openvair.modules.network.domain.exceptions import (
    NetplanFileNotFoundException,
)
from openvair.modules.network.domain.utils.netplan_manager import (
    NetplanManager,
)

LOG = get_logger(__name__)


class NetplanInterface(BaseOVSBridge):
    """Netplan-based implementation of the network bridge interface.

    This class provides methods to create and delete network bridges using
    Netplan for configuration management. It relies on `NetplanManager` for
    handling the YAML configuration files.

    Attributes:
        netplan_manager (NetplanManager): Instance for managing Netplan
            configurations.
        main_port (str): The name of the main network port.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the NetplanInterface instance."""
        super(NetplanInterface, self).__init__(*args, **kwargs)
        self.netplan_manager = NetplanManager()
        self.main_port: str = self.ip_manager.get_main_port_name()
        self.default_route = self.ip_manager.get_default_gateway_ip()

    def create(self, data: Dict) -> None:
        """Create a new interface bridge.

        This method creates a new ovs bridge based on the provided data
        and applies the configuration using Netplan.

        Args:
            data (Dict): Data about the new network bridge. If the 'ip'
                field is provided, it will be modified to include a /24 subnet
                mask.
        """
        LOG.info(f'Start creating bridge: {data["name"]}')

        if not self._is_main_port_file_exist():
            main_port_file = self._create_iface_file(self.main_port)
            main_port_file = self.netplan_manager.rename_file_as_main_port(
                main_port_file
            )
        else:
            main_port_file = self.netplan_manager.get_path_yaml(self.main_port)
            self.netplan_manager.backup_iface_yaml(main_port_file)

        if data.get('ip'):
            data['addresses'] = [f"{data.pop('ip', [])}/24"]

        if self.interfaces:
            LOG.info('Need to prepair interfaces...')
            self._prepare_ifaces_for_creating(data)
            data['interfaces'] = [iface['name'] for iface in data['interfaces']]

        self.netplan_manager.create_ovs_bridge_yaml_file(data)
        self.netplan_manager.apply()

    def delete(self) -> None:
        """Delete a network bridge.

        This method deletes an existing OVS bridge configuration using Netplan
        by removing its YAML file and applying the changes.
        """
        bridge_file = self.netplan_manager.get_path_yaml(self.name)
        bridge_data = self.netplan_manager.get_bridge_data_from_yaml(
            self.name, bridge_file
        )
        if bridge_data.get('interfaces'):
            self._prepare_ifaces_for_deleting(bridge_data)
        self.netplan_manager.delete_iface_yaml(bridge_file)
        self.netplan_manager.apply()

    def _prepare_ifaces_for_creating(self, bridge_data: Dict) -> None:
        """Prepare interfaces for bridge configuration.

        This method retrieves and updates the configuration of network
        interfaces that will be attached to the bridge. It also backs up
        existing YAML configuration files or creates new ones if necessary.

        Args:
            bridge_data (Dict): The data of the bridge.
        """
        LOG.info('Prepairing interfaces...')
        for interface in self.interfaces:
            iface_name: str = interface['name']
            try:
                iface_file = self.netplan_manager.get_path_yaml(iface_name)
            except NetplanFileNotFoundException as err:
                LOG.info(err)
                iface_file = self._create_iface_file(iface_name)

            iface_data = self.netplan_manager.get_iface_data_from_yaml(
                iface_name,
                iface_file,
            )
            if self.main_port == iface_name:
                LOG.info(f'Bridge containing main inetrface: {iface_name}')
                self._move_main_port_params_into_bridge(bridge_data, iface_data)

            self.netplan_manager.change_iface_yaml_file(
                iface_name,
                iface_file,
                iface_data,
            )
        LOG.info('Interfaces prepaired!')

    def _prepare_ifaces_for_deleting(self, bridge_data: Dict) -> None:
        """Restore the network interfaces before bridge deletion.

        This method restores the original configuration of the network
        interfaces after the bridge is deleted by restoring their backup files.

        Args:
            bridge_data (Dict): The data of the bridge.
        """
        for iface_name in bridge_data['interfaces']:
            try:
                # I think it will be necessary to work on stability in this bloc
                # May be need to check if file have another ifaces and check
                # configuration for this iface in antoher files
                LOG.info(f'Restoring backup file for {iface_name}')
                iface_file = self.netplan_manager.get_path_yaml(iface_name)
            except NetplanFileNotFoundException as err:
                LOG.error(err)
                raise

            try:
                iface_bkp_file = self.netplan_manager.get_bkp_path_yaml(
                    iface_name
                )
                self.netplan_manager.delete_iface_yaml(iface_file)
                self.netplan_manager.restore_backup_file(iface_bkp_file)
                LOG.info('File was restored')
            except NetplanFileNotFoundException as err:
                LOG.info(f'Bkp file not exist: {err}')
                if self._is_main_port(iface_name):
                    LOG.info('Restoring main port')
                    iface_data = self.netplan_manager.get_iface_data_from_yaml(
                        iface_name,
                        iface_file,
                    )
                    self._move_iface_params_from_bridge(bridge_data, iface_data)
                    self.netplan_manager.change_iface_yaml_file(
                        iface_name,
                        iface_file,
                        iface_data,
                    )
                else:
                    iface_file.unlink()

    def _move_main_port_params_into_bridge(
        self,
        bridge_data: Dict,
        main_iface_data: Dict,
    ) -> None:
        """Edit bridge and main port configuration.

        This method transfers important network settings (e.g., IP addresses,
        routes, DNS settings) from the main network interface to the bridge.

        Args:
            bridge_data (Dict): The br
                iface_file,
                iface_data,
            )
        except NetplanFileNotFoundException:
            LOG.info(f'File for {iface_name} not found and will be create')
            iface_file = self.netpidge configuration data.
            main_iface_data (Dict): The main interface configuration data.
        """
        LOG.info('Start moving params into bridge config...')
        try:
            bridge_data['nameservers'] = main_iface_data.pop('nameservers', [])

            bridge_data['dhcp4'] = main_iface_data.pop('dhcp4', False)
            bridge_data['routes'] = main_iface_data.pop('routes', [])
            gateway4 = main_iface_data.pop('gateway4', None)
            if gateway4:
                bridge_data['routes'].append({'to': 'default', 'via': gateway4})

            bridge_data['addresses'] = list(
                set(
                    bridge_data.pop('addresses', [])
                    + main_iface_data.pop('addresses', [])
                )
            )

            main_iface_data['dhcp4'] = False

        except Exception as err:
            LOG.error(err)
            raise

    def _move_iface_params_from_bridge(
        self,
        bridge_data: Dict,
        iface_data: Dict,
    ) -> None:
        LOG.info('Start moving params into port from bridge...')
        params_for_move = ['nameservers', 'dhcp4', 'routes', 'addresses']
        if bridge_data.get('dhcp4'):
            params_for_move.remove('addresses')
        while bridge_data:
            k, v = bridge_data.popitem()
            if k in params_for_move:
                iface_data[k] = v

    def _turn_on_dhcp4_for_iface(
        self,
        iface_name: str,
    ) -> None:
        """Enable DHCP4 on the main network interface.

        This method enables DHCP4 for the interface, modifying its YAML
        configuration file. If interface haven't static addresses

        Args:
            iface_name (str): The name of the main network interface.
        """
        try:
            iface_file = self.netplan_manager.get_path_yaml(iface_name)
            iface_data = self.netplan_manager.get_iface_data_from_yaml(
                iface_name,
                iface_file,
            )
            iface_data['dhcp4'] = True
            self.netplan_manager.change_iface_yaml_file(
                iface_name,
                iface_file,
                iface_data,
            )
        except NetplanFileNotFoundException:
            LOG.info(f'File for {iface_name} not found and will be create')
            iface_file = self.netplan_manager.create_iface_yaml(
                iface_name,
                data={'dhcp4': True},
            )
            LOG.info(f'Main port file: {iface_file}')

    def _is_main_port_file_exist(self) -> bool:
        """Check exist of main_port netpan file and return bool"""
        LOG.info('Checking netplan file existense for main port...')
        try:
            file = self.netplan_manager.get_path_yaml(self.main_port)
        except NetplanFileNotFoundException:
            LOG.info('File for main port not exists')
            return False
        else:
            LOG.info(f'File exists: {file}')
            return True

    def _is_main_port(self, iface_name: str) -> bool:
        file = self.netplan_manager.get_path_yaml(iface_name)
        return 'MAIN_PORT.yaml' in str(file.name)

    def _collect_iface_info(self, iface_name: str) -> Dict[str, Any]:
        LOG.info(f'Collecting info from {iface_name}...')
        iface_info: Dict[str, Any] = {}
        ip = self.ip_manager.get_iface_ip(iface_name)
        dhcp4 = self.ip_manager.is_dhcp_ip(iface_name)
        iface_info['dhcp4'] = dhcp4
        if not dhcp4:
            iface_info['addresses'] = [f'{ip}/24'] if ip else None
            if iface_name == self.main_port:
                iface_info['routes'] = [
                    {'to': 'default', 'via': self.default_route}
                ]
                iface_info['nameservers'] = {'addresses': [self.default_route]}

        LOG.info(f'Info from {iface_name}: {iface_info}')
        return iface_info

    def _create_iface_file(self, iface_name: str) -> Path:
        iface_info = self._collect_iface_info(iface_name)
        return self.netplan_manager.create_iface_yaml(
            iface_name,
            data=iface_info,
        )
