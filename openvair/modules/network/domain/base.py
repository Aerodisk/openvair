"""Base classes for network domain entities.

This module defines abstract base classes and concrete implementations for
network interfaces and bridges. It also includes a class for managing virtual
networks using Libvirt.

Classes:
    BaseInterface: Abstract base class for network interfaces.
    BaseBridge: Abstract base class for network bridges.
    BaseOVSBridge: Abstract base class for OVS bridges.
"""

from __future__ import annotations

import abc
import uuid
from typing import Any, Dict, List

from openvair.libs.log import get_logger
from openvair.modules.network.domain.utils.ip_manager import IPManager
from openvair.modules.network.domain.utils.ovs_manager import OVSManager

LOG = get_logger(__name__)


class BaseInterface(metaclass=abc.ABCMeta):
    """Abstract base class for network interfaces."""

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a network interface."""
        self.id = str(kwargs.get('id', uuid.uuid4()))
        self.name = kwargs.get('name', '')
        self.mac = kwargs.get('mac', '')
        self.ip = kwargs.get('ip', '')
        self.netmask = kwargs.get('netmask', '')
        self.gateway = kwargs.get('gateway', '')
        self.inf_type = kwargs.get('inf_type', '')
        self.status = kwargs.get('status', '')
        self.power_state = kwargs.get('power_state', '')

    @abc.abstractmethod
    def enable(self) -> None:
        """Enable the network interface."""
        ...

    @abc.abstractmethod
    def disable(self) -> None:
        """Disable the network interface."""
        ...


class BaseBridge(metaclass=abc.ABCMeta):
    """Abstract base class for network bridges."""

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a network bridge."""
        self.id = str(kwargs.get('id', uuid.uuid4()))
        self.name = str(kwargs.pop('name', ''))
        self.type = str(kwargs.pop('type', 'bridge'))
        self.interfaces: List[Dict] = list(kwargs.pop('interfaces', []))

    @abc.abstractmethod
    def create(self, data: Dict) -> None:
        """Create a network bridge."""
        ...

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the network bridge."""
        ...

    @abc.abstractmethod
    def get_bridges_list(self) -> List[Dict]:
        """Get a list of all network bridges."""
        ...


class BaseOVSBridge(BaseBridge):
    """Abstract base class for OVS bridges.

    This class extends the BaseBridge class and provides additional
    functionality specific to Open vSwitch (OVS) bridges, using `OVSManager`
    and `IPManager` to manage OVS and IP configurations.

    Attributes:
        ovs_manager (OVSManager): Instance of OVSManager used to manage
            OVS-related operations.
        ip_manager (IPManager): Instance of IPManager used to manage IP-related
            operations for the bridge.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize an OVS bridge.

        This constructor initializes the OVSManager and IPManager instances
        for managing Open vSwitch and network configurations.

        Args:
            **kwargs: Arbitrary keyword arguments for initializing the bridge
                properties like name, type, and interfaces.
        """
        super().__init__(**kwargs)
        self.ovs_manager = OVSManager()
        self.ip_manager = IPManager()

    @abc.abstractmethod
    def create(self, data: Dict) -> None:
        """Create a ovs bridge."""
        ...

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the ovs bridge."""
        ...

    def get_bridges_list(self) -> List[Dict]:
        """Retrieve the list of network bridges.

        This method gathers bridge information from OVS and Linux network
        interfaces, returning a list of ovs bridges.

        Returns:
            List: A list of network bridges.
        """
        LOG.info('Start getting the list of bridges')
        ovs_bridges_info = self.ovs_manager.get_bridges()
        linux_interfaces_data = self.ip_manager.get_json_ifaces()

        # Find index of OVS bridge name in bridge-info list
        name_index = ovs_bridges_info['headings'].index('name')

        # Collect all OVS bridge names from ovs_bridges_info["data"]
        ovs_bridges_names = [
            bridge[name_index] for bridge in ovs_bridges_info['data']
        ]

        # Collect OVS bridge info from Linux interfaces info
        LOG.info('Finished getting the list of bridges')
        return [
            iface
            for iface in linux_interfaces_data
            if iface['ifname'] in ovs_bridges_names
            or iface['ifname'] == 'virbr0'
        ]
