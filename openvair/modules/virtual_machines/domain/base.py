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

from openvair.libs.log import get_logger
from openvair.libs.libvirt.connection import LibvirtConnection
from openvair.libs.data_handlers.xml.exceptions import XMLDeserializationError
from openvair.libs.data_handlers.xml.serializer import deserialize_xml
from openvair.modules.virtual_machines.domain.exceptions import (
    GraphicPortNotFoundInXmlException,
    GraphicTypeNotFoundInXmlException,
)
from openvair.modules.virtual_machines.libs.template_rendering.vm_renderer import (  # noqa: E501
    VMRenderer,
)

LOG = get_logger(__name__)


class BaseVMDriver:
    """Abstract base class for virtual machine drivers.

    This class defines the basic interface for virtual machine drivers,
    requiring implementations of methods to start, stop, access a
    VNC session for a virtual machine, create, delete and revert to
    snapshot of the virtual machine.
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

    @abc.abstractmethod
    def create_snapshot(self) -> None:
        """Create a snapshot of the virtual machine."""
        pass

    @abc.abstractmethod
    def revert_snapshot(self) -> None:
        """Revert to a snapshot of the virtual machine."""
        pass


class BaseLibvirtDriver(BaseVMDriver):
    """Base class for Libvirt-based virtual machine drivers.

    This class provides common functionality for Libvirt-based virtual
    machine drivers, including methods for rendering domain and network
    XML templates, and extracting graphics information from domain XML.

    Attributes:
        connection (LibvirtConnection): Connection to the Libvirt API.
        vm_info (Dict): Dictionary containing the virtual machine
            configuration.
        snapshot_info (Dict): Dictionary containing the snapshot configuration.
    """

    def __init__(self) -> None:
        """Initialize the BaseLibvirtDriver.

        Sets up the Jinja2 environment for template rendering and
        initializes the connection to Libvirt.
        """
        self.renderer = VMRenderer()
        self.connection = LibvirtConnection()
        self.vm_info: Dict = {}
        self.snapshot_info: Dict = {}

    def render_domain(self, vm_info: Dict) -> str:
        """Render the domain XML from the virtual machine information.

        Args:
            vm_info (Dict): Dictionary containing the virtual machine
                configuration.

        Returns:
            str: The rendered domain XML as a string.
        """
        return self.renderer.render_domain({'domain': vm_info})

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
        """Extract the port number of the graphics device from the domain XML.

        This method parses the provided domain XML and retrieves the `port`
        attribute from the `<graphics>` element inside `<devices>`.

        Args:
            domain_xml (str): The domain XML as a string.

        Returns:
            Optional[str]: The port number as a string, or None if not found.

        Raises:
            GraphicPortNotFoundInXmlException: If the graphics port is missing
                or the XML is invalid.
        """
        port: Optional[str]
        try:
            parsed_xml = deserialize_xml(domain_xml)
            graphics_device = parsed_xml['domain']['devices']['graphics']
            port = graphics_device.get('@port')
        except (KeyError, AttributeError, TypeError, XMLDeserializationError):
            err = GraphicPortNotFoundInXmlException(domain_xml)
            LOG.error(err)
            raise err
        else:
            return str(port) if port is not None else None

    @staticmethod
    def _get_graphic_type_from_xml(domain_xml: str) -> Optional[str]:
        """Extract the type of the graphics device from the domain XML.

        This method parses the provided domain XML and retrieves the `type`
        attribute from the `<graphics>` element inside `<devices>`.

        Args:
            domain_xml (str): The domain XML as a string.

        Returns:
            Optional[str]: The graphics type as a string, or None if not found.

        Raises:
            GraphicTypeNotFoundInXmlException: If the graphics type is missing
                or the XML is invalid.
        """
        graphics_type: Optional[str]
        try:
            parsed_xml = deserialize_xml(domain_xml)
            graphics_device = parsed_xml['domain']['devices']['graphics']
            graphics_type = graphics_device.get('@type')
        except (KeyError, AttributeError, TypeError, XMLDeserializationError):
            err = GraphicTypeNotFoundInXmlException(domain_xml)
            LOG.error(err)
            raise err
        else:
            return graphics_type

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
            f"{self.vm_info.get('name', '')}"
        )

    def create_snapshot(self) -> None:
        """Create a snapshot of the virtual machine.

        Type of snapshot in snapshot_info: None|'internal'|'external',
        None is 'internal' by default.
        """
        snapshot_type = self.snapshot_info.get('type')
        if snapshot_type == 'external':
            return self.create_external_snapshot()
        return self.create_internal_snapshot()

    def create_internal_snapshot(self) -> None:
        """Create an internal snapshot of the virtual machine.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def create_external_snapshot(self) -> None:
        """Create an external snapshot of the virtual machine.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def revert_snapshot(self) -> None:
        """Revert to a snapshot of the virtual machine.

        Type of snapshot in snapshot_info: None|'internal'|'external',
        None is 'internal' by default.
        """
        snapshot_type = self.snapshot_info.get('type')
        if snapshot_type == 'external':
            return self.revert_external_snapshot()
        return self.revert_internal_snapshot()

    def revert_internal_snapshot(self) -> None:
        """Revert to an internal snapshot of the virtual machine.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def revert_external_snapshot(self) -> None:
        """Revert to an external snapshot of the virtual machine.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError
