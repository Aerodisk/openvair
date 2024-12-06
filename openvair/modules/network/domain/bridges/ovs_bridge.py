"""Implementation of virtual network management using Open vSwitch.

This module provides an implementation of the network bridge interface using
Open vSwitch (OVS) for managing virtual network bridges and interfaces.

Classes:
    OVSInterface: Implementation of the network bridge interface using OVS.
"""

from typing import Any, Dict

from openvair.libs.log import get_logger
from openvair.modules.network.domain.base import BaseOVSBridge
from openvair.modules.network.domain.utils.exceptions import (
    OVSManagerException,
)

LOG = get_logger(__name__)


class OVSInterface(BaseOVSBridge):
    """Implementation of the network bridge interface using OVS.

    This class provides methods to create and delete network bridges using
    Open vSwitch (OVS) or Netplan, depending on the configuration.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the OVSInterface instance.

        This constructor initializes the OVS manager and selects the appropriate
        configuration manager based on the network configuration. It also
        retrieves and stores the name of the main network interface
        (`main_port`).
        """
        super().__init__(**kwargs)
        self.main_port: str = self.ip_manager.get_main_port_name()
        self.default_route = self.ip_manager.get_default_gateway_ip()

    def create(self, data: Dict) -> None:
        """Create a new interface bridge.

        This method creates a new network bridge using the selected
        configuration manager, activates the interface, and applies the
        configuration. Optionally, it assigns an IP address to the bridge if
        provided.

        Args:
            data (Dict): Data about the new network bridge, including optional
                IP address.
        """
        try:
            self.ovs_manager.create_bridge(self.name)
            self.ip_manager.turn_on_interface(self.name)

            # Add custom IP address if it was specified

            for iface in self.interfaces:
                LOG.info(iface)
                iface_name: str = iface.get('name', '')
                if iface_name == self.main_port and not self._is_bridge(
                    iface_name
                ):
                    self.ip_manager.run_dhclient(self.main_port)
                    self._configure_main_port()
                self.ovs_manager.add_interface(self.name, iface_name)

            ip = data.get('ip')
            if ip:
                self.ip_manager.set_ip(self.name, f'{ip}/24')

        except OVSManagerException as error:
            LOG.error(f'Failed to create interface bridge: {error}')
            self._rollback_on_failure()
            raise

    def delete(self) -> None:
        """Delete a network bridge.

        This method deletes an existing OVS bridge and its configuration using
        the selected configuration manager. If the main network interface has no
        IP address after the bridge deletion, it runs a DHCP client to assign
        a new IP address.
        """
        LOG.info(f'Start deleting bridge {self.name}')
        bridge_ifaces = self.ovs_manager.get_ports_in_bridge(self.name)
        for iface_name in bridge_ifaces:
            iface_data = self.ip_manager.get_iface_data(iface_name)
            LOG.info('@@@')
            LOG.info(iface_data)
            if iface_data.get('ifalias') == 'MAIN':
                LOG.info(f'Bridge contain main port: {iface_name}')
                self._restore_main_port(iface_name)
        self.ovs_manager.delete_bridge(self.name)

    def _configure_main_port(
        self,
    ) -> None:
        """Move the IP address from the main interface to the bridge interface.

        This method retrieves the IP address of the main interface, sets it on
        the bridge interface, and configures the default gateway accordingly.

        Raises:
            OVSManagerException: If the main port configuration fails.
        """
        try:
            LOG.info('The main port was added into the bridge')
            main_port_ip = self.ip_manager.get_iface_ip(self.main_port)
            self.ip_manager.flush_iface_ip(self.main_port)
            self.ip_manager.set_ip(self.name, f'{main_port_ip}/24')
            self.ip_manager.set_default_gateway(self.default_route)
            self.ip_manager.set_alias(self.main_port, 'MAIN')
            LOG.info('Main port ip was moved to the bridge')
        except Exception as error:
            LOG.error(f'Failed to configure the main port: {error}')
            msg = 'Failed to configure the main port'
            raise OVSManagerException(msg) from error

    def _restore_main_port(self, iface_name: str) -> None:
        LOG.info('Restoring main port..')
        ip = self.ip_manager.get_iface_ip(self.name)
        if ip:
            LOG.info('Moving ip from bridge...')
            self.ip_manager.set_ip(iface_name, f'{ip}/24')
        else:
            LOG.info('Starting dhcp for main port...')
            self.ip_manager.run_dhclient(self.main_port)

        self.ip_manager.flush_iface_ip(self.name)
        self.ip_manager.set_default_gateway(self.default_route)

    def _restart_port(self, iface_name: str) -> None:
        LOG.info(f'Restatring interface {iface_name}...')
        self.ip_manager.turn_off_interface(iface_name)
        self.ip_manager.turn_on_interface(iface_name)

    def _rollback_on_failure(self) -> None:
        """Rollback changes in case of failure.

        This method deletes the OVS bridge and its configuration if the bridge
        creation process fails. It also runs a DHCP client to reassign an IP
        address to the main network interface if necessary.
        """
        LOG.info('Rolling back changes due to failure')
        self.ovs_manager.delete_bridge(self.name)
        if not self.ip_manager.get_iface_ip(self.main_port):
            self.ip_manager.run_dhclient(self.main_port)

    def _is_bridge(self, iface_name: str) -> bool:
        bridges = self.get_bridges_list()
        return any(bridge['ifname'] == iface_name for bridge in bridges)
