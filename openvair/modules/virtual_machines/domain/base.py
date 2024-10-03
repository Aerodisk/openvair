"""Base classes for virtual machine drivers.

This module provides abstract base classes and utility methods for
implementing virtual machine drivers. It includes a base class for
Libvirt-based drivers, which provides common functionality such as
rendering XML templates and extracting graphics information from the
domain XML.

Classes:
    BaseVMDriver: Abstract base class defining the interface for virtual
        machine drivers.
    BaseLibvirtDriver: Base class for Libvirt-based virtual machine
        drivers, providing common functionality such as template rendering
        and graphics information extraction.
"""

import abc
from typing import Dict, Optional
from xml.etree import ElementTree

from jinja2 import Environment, FileSystemLoader, select_autoescape

from openvair.modules.tools.libvirt_utils import LibvirtConnection
from openvair.modules.virtual_machines.config import TEMPLATES_PATH


class BaseVMDriver:
    """Abstract base class for virtual machine drivers.

    This class defines the basic interface for virtual machine drivers,
    requiring implementations of methods to start, stop, and access a
    VNC session for a virtual machine.
    """

    @abc.abstractmethod
    def start(self) -> Dict:
        """Start the virtual machine.

        Returns:
            Dict: A dictionary containing the result of the start
            operation.
        """
        pass

    @abc.abstractmethod
    def turn_off(self) -> Dict:
        """Turn off the virtual machine.

        Returns:
            Dict: A dictionary containing the result of the turn-off
            operation.
        """
        pass

    @abc.abstractmethod
    def vnc(self) -> Dict:
        """Start a VNC session for the virtual machine.

        Returns:
            Dict: A dictionary containing the URL of the VNC session.
        """
        pass


class BaseLibvirtDriver(BaseVMDriver):
    """Base class for Libvirt-based virtual machine drivers.

    This class provides common functionality for Libvirt-based virtual
    machine drivers, including methods for rendering domain and network
    XML templates, and extracting graphics information from domain XML.

    Attributes:
        env (Environment): Jinja2 environment for loading templates.
        domain_template (Template): Jinja2 template for domain XML.
        connection (LibvirtConnection): Connection to the Libvirt API.
        vm_info (Dict): Dictionary containing the virtual machine
            configuration.
    """

    def __init__(self):
        """Initialize the BaseLibvirtDriver.

        Sets up the Jinja2 environment for template rendering and
        initializes the connection to Libvirt.
        """
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_PATH),
            autoescape=select_autoescape(['xml']),
        )
        self.domain_template = self.env.get_template('domain.xml')
        self.connection = LibvirtConnection()
        self.vm_info = {}

    def render_domain(self, vm_info: Dict) -> str:
        """Render the domain XML from the virtual machine information.

        Args:
            vm_info (Dict): Dictionary containing the virtual machine
                configuration.

        Returns:
            str: The rendered domain XML as a string.
        """
        return self.domain_template.render(domain=vm_info)

    def render_network(self, network_info: Dict) -> str:
        """Render the network XML from the network information.

        Args:
            network_info (Dict): Dictionary containing the network
                configuration.

        Returns:
            str: The rendered network XML as a string.
        """
        return self.network_template.render(network=network_info)

    def start(self) -> Dict:
        """Start the virtual machine.

        This method should be implemented by subclasses.

        Returns:
            Dict: A dictionary containing the result of the start
            operation.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def turn_off(self) -> Dict:
        """Turn off the virtual machine.

        This method should be implemented by subclasses.

        Returns:
            Dict: A dictionary containing the result of the turn-off
            operation.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def vnc(self) -> Dict:
        """Start a VNC session for the virtual machine.

        This method should be implemented by subclasses.

        Returns:
            Dict: A dictionary containing the URL of the VNC session.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @staticmethod
    def _get_graphic_port_from_xml(domain_xml: str) -> Optional[str]:
        """Extract the graphic port from the domain XML.

        Args:
            domain_xml (str): The domain XML as a string.

        Returns:
            Optional[int]: The graphic port number, or None if not found.
        """
        try:
            root = ElementTree.fromstring(domain_xml)  # noqa: S314 because for fix it need oiter library
            grafics_device = root.find('./devices/graphics')
            if grafics_device:
                return grafics_device.get('port')
        except ElementTree.ParseError:
            return None

    @staticmethod
    def _get_graphic_type_from_xml(domain_xml: str) -> Optional[str]:
        """Extract the graphic type from the domain XML.

        Args:
            domain_xml (str): The domain XML as a string.

        Returns:
            Optional[str]: The graphic type, or an empty string if not
            found.
        """
        try:
            root = ElementTree.fromstring(domain_xml)  # noqa: S314 because for fix it need oiter library
            grafics_device = root.find('./devices/graphics')
            if grafics_device:
                return grafics_device.get('type')
        except ElementTree.ParseError:
            return ''

    def _get_graphic_url(self, domain_xml: str) -> Optional[str]:
        """Generate the graphic URL from the domain XML.

        Args:
            domain_xml (str): The domain XML as a string.

        Returns:
            Optional[str]: The graphic URL.
        """
        ip = '0.0.0.0'  # noqa: S104
        graphic_type = self._get_graphic_type_from_xml(domain_xml)
        return (
            f"http://{ip}/{graphic_type}/?token="
            f"{self.vm_info.get('name', '')}")
