"""Base classes for network domain entities.

This module defines abstract base classes and concrete implementations for
network interfaces and bridges. It also includes a class for managing virtual
networks using Libvirt.

Classes:
    BaseInterface: Abstract base class for network interfaces.
    BaseBridge: Abstract base class for network bridges.
    Interface: Concrete implementation of a network interface.
    Bridge: Concrete implementation of a network bridge.
    VirshNetwork: Class for managing virtual networks with Libvirt.
"""

from __future__ import annotations

import abc
import uuid
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from openvair.libs.log import get_logger
from openvair.modules.network.config import TEMPLATES_PATH
from openvair.modules.tools.libvirt_utils import LibvirtConnection

LOG = get_logger(__name__)


class BaseInterface(metaclass=abc.ABCMeta):
    """Abstract base class for network interfaces."""

    def __init__(self, **kwargs):
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

    def __init__(self, **kwargs):
        """Initialize a network bridge."""
        self.id = str(kwargs.get('id', uuid.uuid4()))
        self.name = kwargs.pop('name', '')
        self.type = kwargs.pop('type', 'bridge')
        self.interfaces = kwargs.pop('interfaces', [])

    @abc.abstractmethod
    def create(self, data: Dict) -> None:
        """Create a network bridge."""
        ...

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the network bridge."""
        ...

    @abc.abstractmethod
    def get_bridges_list(self) -> List:
        """Get a list of all network bridges."""
        ...


class Interface(BaseInterface):
    """Concrete implementation of a network interface."""

    def __init__(self, *args, **kwargs):
        """Initialize the Interface."""
        super(Interface, self).__init__(*args, **kwargs)

    def enable(self) -> None:
        """Enable the network interface."""
        raise NotImplementedError

    def disable(self) -> None:
        """Disable the network interface."""
        raise NotImplementedError


class Bridge(BaseBridge):
    """Concrete implementation of a network bridge."""

    def __init__(self, *args, **kwargs):
        """Initialize the Bridge."""
        super(Bridge, self).__init__(*args, **kwargs)

    def create(self, data: Dict) -> None:
        """Create a network bridge."""
        raise NotImplementedError

    def delete(self) -> None:
        """Delete the network bridge."""
        raise NotImplementedError

    def get_bridges_list(self) -> List:
        """Get a list of all network bridges."""
        raise NotImplementedError


class VirshNetwork:
    """Class for managing virtual networks with Libvirt."""

    def __init__(self):
        """Initialize the VirshNetwork with template and Libvirt connection."""
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_PATH),
            autoescape=select_autoescape(['xml']),
        )
        self.network_template = self.env.get_template('network.xml')
        self.connection = LibvirtConnection()

    def render_network(self, network_info: Dict) -> str:
        """Render network XML from template with provided network info.

        Args:
            network_info (Dict): A dictionary containing network information.

        Returns:
            str: The rendered network XML as a string.
        """
        return self.network_template.render(network=network_info)

    def net_define(self, network_info: Dict) -> None:
        """Define and start a network based on provided network info.

        Args:
            network_info (Dict): A dictionary containing network information.
        """
        network_xml = self.render_network(network_info)
        with self.connection as connection:
            network = connection.networkDefineXML(network_xml)
            network.create()
            network.setAutostart(1)

    def net_undefine(self, network_name: str) -> None:
        """Undefine and destroy a network by name.

        Args:
            network_name (str): The name of the network to undefine.
        """
        with self.connection as connection:
            network = connection.networkLookupByName(network_name)
            if network.isActive():
                network.destroy()
            network.undefine()
