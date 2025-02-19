"""Adapter for interacting with virtual networks using libvirt's virsh utility.

This module provides the `VirshAdapter` class, which is used to manage
virtual networks through the libvirt API.

Classes:
    - VirshAdapter: Adapter class for managing virtual networks.
"""

from typing import List, Optional, cast

from libvirt import libvirtError

from openvair.libs.log import get_logger
from openvair.libs.libvirt.connection import LibvirtConnection

LOG = get_logger(__name__)


class VirshNetworkAdapter:
    """Adapter class for interacting with virtual networks using virsh utility.

    Attributes:
        connection (LibvirtConnection): The libvirt connection object.
    """

    def __init__(self) -> None:
        """Initialize the VirshAdapter."""
        self.connection = LibvirtConnection()

    def get_virt_network_names(self) -> List[str]:
        """Retrieves list of names virtual networks."""
        LOG.info('Getting virtual_networks from virsh...')
        with self.connection as connection:
            return list(connection.listNetworks())

    def define_network(
        self,
        virtual_network_xml: str,
        *,
        auto_start: bool = True,
    ) -> None:
        """Defines a virtual network.

        Args:
            virtual_network_xml (str): The XML configuration of the virtual
                network.
            auto_start (bool, optional): Whether to automatically start the
                virtual network. Defaults to True.
        """
        LOG.info('Define virtual network...')

        with self.connection as connection:
            network = connection.networkDefineXML(virtual_network_xml)
            if auto_start:
                network.setAutostart(1)

        LOG.info('Define virtual network complete')

    def undefine_network(self, vn_id: str) -> None:
        """Undefines a virtual network.

        Args:
            vn_id (str): The UUID of the virtual network to undefine.
        """
        LOG.info(f'Undefining virtual network {vn_id}...')

        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            network.undefine()

        LOG.info(f'Undefining virtual network {vn_id} complete')

    def disable_network(self, vn_id: str) -> None:
        """Disables a virtual network.

        Args:
            vn_id (str): The UUID of the virtual network to disable.
        """
        LOG.info(f'Disabling virtual network {vn_id}...')

        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            if network.isActive():
                network.destroy()

        LOG.info(f'Disabling virtual network {vn_id} complete')

    def enable_network(self, vn_id: str) -> None:
        """Enables a virtual network.

        Args:
            vn_id (str): The UUID of the virtual network to enable.
        """
        LOG.info(f'Enabling virtual network {vn_id}...')

        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            if not network.isActive():
                network.create()

        LOG.info(f'Enabling virtual network {vn_id} complete')

    def get_network_xml_by_name(self, vn_name: str) -> str:
        """Retrieves the XML configuration of a virtual network by name.

        Args:
            vn_name (str): The name of the virtual network.

        Returns:
            str: The XML configuration of the virtual network.
        """
        LOG.info('Getting virtual network XML from virsh...')

        with self.connection as connection:
            network = connection.networkLookupByName(vn_name)

        LOG.info('Getting virtual network XML from virsh complete')
        return cast(str, network.XMLDesc())

    def get_network_xml_by_uuid(self, network_uuid: str) -> str:
        """Retrieves the XML configuration of a virtual network by UUID.

        Args:
            network_uuid (str): The UUID of the virtual network.

        Returns:
            str: The XML configuration of the virtual network.
        """
        LOG.info('Getting virtual network XML from virsh...')

        with self.connection as connection:
            network = connection.networkLookupByUUIDString(network_uuid)

        LOG.info('Getting virtual network XML from virsh complete')
        return cast(str, network.XMLDesc())

    def is_network_exist_by_name(self, network_name: str) -> bool:
        """Checks if a virtual network exists by name.

        Args:
            network_name (str): The name of the virtual network.

        Returns:
            bool: True if the virtual network exists, False otherwise.
        """
        LOG.info('Checking virtual network in virsh...')
        with self.connection as connection:
            try:
                connection.networkLookupByName(network_name)
            except libvirtError:
                return False
            else:
                return True

    def is_network_exist_by_uuid(self, network_id: str) -> Optional[bool]:
        """Checks if a virtual network exists by UUID.

        Args:
            network_id (str): The UUID of the virtual network.

        Returns:
            bool: True if the virtual network exists, False otherwise.
        """
        LOG.info('Checking virtual network in virsh...')
        with self.connection as connection:
            try:
                connection.networkLookupByUUIDString(network_id)
            except libvirtError:
                return False
            else:
                return True

    def get_network_state(self, vn_id: str) -> str:
        """Retrieves the state of a virtual network.

        Args:
            vn_id (str): The UUID of the virtual network.

        Returns:
            str: The state of the virtual network ('active' or 'inactive').
        """
        LOG.info('Retrieving state of virtual network in virsh...')
        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            if network.isActive():
                LOG.info('State is active')
                return 'active'

            LOG.info('State is inactive')
            return 'inactive'

    def get_network_persistent(self, vn_id: str) -> str:
        """Retrieves the persistence status of a virtual network.

        Args:
            vn_id (str): The UUID of the virtual network.

        Returns:
            str: The persistence status of the virtual network ('yes' if
                persistent, 'no' otherwise).
        """
        LOG.info('Retrieving persistence status of virtual network in virsh...')
        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            if network.isPersistent():
                LOG.info('State is persistent')
                return 'yes'

            LOG.info('State is not persistent')
            return 'no'

    def get_network_autostart(self, vn_id: str) -> str:
        """Retrieves the autostart status of a virtual network.

        Args:
            vn_id (str): The UUID of the virtual network.

        Returns:
            str: The autostart status of the virtual network ('yes' if autostart
                is enabled, 'no' otherwise).
        """
        LOG.info('Retrieving autostart status of virtual network in virsh...')
        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            if network.isPersistent():
                LOG.info('State is persistent')
                return 'yes'

            LOG.info('State is not persistent')
            return 'no'

    def get_network_uuid(self, network_name: str) -> str:
        """Retrieves the UUID of a virtual network by name.

        Args:
            network_name (str): The name of the virtual network.

        Returns:
            str: The UUID of the virtual network.
        """
        LOG.info('Retrieving UUID string of virtual network in virsh...')
        with self.connection as connection:
            network = connection.networkLookupByName(network_name)
            uuid_str: str = network.UUIDString()

            LOG.info('UUID string retrieved')
            return uuid_str

    def get_network_name(self, vn_id: str) -> str:
        """Retrieves the name of a virtual network by UUID.

        Args:
            vn_id (str): The UUID of the virtual network.

        Returns:
            str: The name of the virtual network.
        """
        LOG.info('Retrieving network name of virtual network in virsh...')
        with self.connection as connection:
            network = connection.networkLookupByUUIDString(vn_id)
            network_name: str = network.name()

            LOG.info('Network name retrieved')
            return network_name

    def get_network_bridge_by_id(self, network_id: str) -> str:
        """Retrieves the bridge name associated with a virtual network by UUID.

        Args:
            network_id (str): The UUID of the virtual network.

        Returns:
            str: The bridge name associated with the virtual network.
        """
        LOG.info(
            f'Retrieving bridge name of virtual {network_id} network in virsh'
        )

        with self.connection as connection:
            network = connection.networkLookupByUUIDString(network_id)
            bridge_name: str = network.bridgeName()

            LOG.info('Bridge name retrieved')
            return bridge_name

    def get_network_bridge_by_name(self, network_name: str) -> str:
        """Retrieves the bridge name associated with a virtual network by name.

        Args:
            network_name (str): The name of the virtual network.

        Returns:
            str: The bridge name associated with the virtual network.
        """
        LOG.info(
            f'Retrieving bridge name of virtual {network_name} network in virsh'
        )

        with self.connection as connection:
            network = connection.networkLookupByName(network_name)
            bridge_name: str = network.bridgeName()

            LOG.info('Bridge name retrieved')
            return bridge_name


if __name__ == '__main__':
    v = VirshNetworkAdapter()
    s = v.get_virt_network_names()
