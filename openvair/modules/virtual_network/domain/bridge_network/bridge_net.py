"""Module for managing bridge virtual networks and port groups.

This module provides classes for managing bridge virtual networks, including
adding and removing port groups, creating and deleting networks, and enabling
or disabling them.

Classes:
    - BridgePortGroup: Represents a port group in a bridge network.
    - BridgeNetwork: Manages the lifecycle of a bridge virtual network.
"""

from typing import Any, Dict, List, cast

from libvirt import libvirtError

from openvair.libs.log import get_logger
from openvair.modules.tools.jinja_tools import xml_collector
from openvair.modules.virtual_network.domain.base import (
    BasePortGroup,
    BaseVirtualNetwork,
)
from openvair.modules.virtual_network.domain.exception import (
    PortGroupException,
    VirshDefineNetworkException,
)

LOG = get_logger(__name__)


class BridgePortGroup(BasePortGroup):
    """Represents a port group in a bridge network."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the BridgePortGroup instance."""
        super().__init__(*args, **kwargs)

    def add_tag(self, tag: str) -> None:
        """Adds a tag to the port group."""
        self.tags = list(self.tags)
        self.tags.append(tag)

    def delete_tag(self, tag: str) -> None:
        """Deletes a tag from the port group."""
        self.tags.remove(tag)


class BridgeNetwork(BaseVirtualNetwork):
    """Represents a bridge virtual network and manages its port groups."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the BridgeNetwork instance."""
        super().__init__(*args, **kwargs)
        self.port_groups: List[BasePortGroup] = [
            BridgePortGroup(**pg) for pg in kwargs.pop('port_groups', [])
        ]

    def add_port_group(self, port_group: Dict) -> Dict[str, Any]:
        """Adds a port group to the bridge network.

        Args:
            port_group (Dict): Information about the port group.

        Returns:
            Dict[str, Any]: Updated network data.
        """
        LOG.info('Adding port group to bridge virtual network...')

        self._check_state()
        self.port_groups.append(BridgePortGroup(**port_group))
        self._define_network()
        LOG.info('Port groups successfully added')
        return self._get_virsh_data()

    def del_port_group_by_name(self, data: Dict) -> Dict[str, str]:
        """Deletes a port group from the bridge network by name.

        Args:
            data (Dict): Data containing the name of the port group.

        Returns:
            Dict[str, Any]: Updated network data.
        """
        LOG.info('Deleting port group from bridge virtual network...')

        self._check_state()
        port_group_name = data.pop('port_group_name')

        for pg in self.port_groups.copy():
            if pg.port_group_name == port_group_name:
                self.port_groups.remove(pg)

        self._define_network()
        virsh_data: Dict[str, str] = self._get_virsh_data()

        LOG.info('Port group successfully deleted')
        return virsh_data

    def create(self) -> Dict[str, str]:
        """Creates the bridge network.

        Returns:
            Dict[str, Any]: Updated network data.
        """
        LOG.info('Creating bridge virtual network...')

        self._define_network()
        virsh_data = self._get_virsh_data()

        LOG.info('Bridge virtual network successfully created')
        return virsh_data

    def delete(self) -> None:
        """Deletes the bridge network."""
        LOG.info('Deleting bridge virtual network...')

        if self.virsh.get_network_state(self.id) == 'active':
            self.virsh.disable_network(self.id)
        self.virsh.undefine_network(self.id)

        LOG.info('Bridge virtual network successfully deleted')

    def enable(self) -> str:
        """Enables the bridge network.

        Returns:
            str: Network state.
        """
        LOG.info('Enabling bridge virtual network...')

        self.virsh.enable_network(self.id)
        state = self.virsh.get_network_state(self.id)

        LOG.info('Bridge virtual network successfully enabled')
        return state

    def disable(self) -> str:
        """Disables the bridge network.

        Returns:
            str: Network state.
        """
        LOG.info('Disabling bridge virtual network...')
        self.virsh.disable_network(self.id)
        state = self.virsh.get_network_state(self.id)

        LOG.info('Bridge virtual network successfully disabled')
        return state

    def add_tag_to_port_group(self, data: Dict) -> Dict[str, Dict[str, str]]:
        """Adds a tag to a port group in the bridge network.

        Args:
            data (Dict): Data containing the tag ID and port group name.

        Returns:
            Dict[str, Dict[str, str]]: Updated network data.
        """
        LOG.info(
            f"Adding tag {data.get('tag_id')} to port group "
            f"{data.get('pg_name')} in bridge virtual network..."
        )

        pg_name = data.pop('pg_name')
        tag_id = data.pop('tag_id')

        self._check_state()
        port_group = self._retrieve_port_group(pg_name)

        LOG.info('Checking if port group is trunk...')
        if port_group.is_trunk == 'no':
            msg = f'Port group {port_group.port_group_name} is not a trunk'
            LOG.error(msg)
            raise PortGroupException(msg)
        LOG.info(f'OK, Port group {pg_name} is trunk. Continue adding...')

        port_group.add_tag(tag_id)
        self._define_network()

        LOG.info(f'Tag {tag_id} successfully added to port group {pg_name}')
        return {
            'virsh_data': self._get_virsh_data(),
            'port_group': port_group.as_dict(),
        }

    def is_exist_in_virsh(self) -> bool:
        """Checks if the network exists in virsh.

        Returns:
            Dict: Network existence information.
        """
        return self.virsh.is_network_exist_by_name(self.network_name)

    def _define_network(self) -> None:
        """Defines the virtual network in virsh."""
        xml_file = xml_collector.create_virtual_network_xml(self.as_dict())
        try:
            self.virsh.define_network(xml_file)
            self.virsh_xml = self.virsh.get_network_xml_by_name(
                self.network_name
            )
        except libvirtError as err:
            msg = f'libvirtError: {err}'
            LOG.error(msg)
            raise VirshDefineNetworkException(msg)

    def _get_virsh_data(self) -> Dict[str, str]:
        """Retrieves data about the network from virsh.

        Returns:
            Dict[str, str]: Network data.
        """
        LOG.info('Retrieving data about the network from virsh')
        return {
            'state': self.virsh.get_network_state(self.id),
            'autostart': self.virsh.get_network_autostart(self.id),
            'persistent': self.virsh.get_network_persistent(self.id),
            'virsh_xml': self.virsh.get_network_xml_by_uuid(self.id),
        }

    def _check_state(self) -> None:
        """Checks the state of the network before making changes."""
        if self.virsh.get_network_state(self.id) == 'active':
            msg = (
                f'Network {self.network_name} is active. '
                'It must be turned off before changing port group.'
            )
            raise VirshDefineNetworkException(msg)

    def _retrieve_port_group(self, pg_name: str) -> BridgePortGroup:
        """Retrieves a port group by name.

        Args:
            pg_name (str): The name of the port group.

        Returns:
            BridgePortGroup: The retrieved port group.

        Raises:
            PortGroupException: If the port group does not exist.
        """
        port_groups = set(
            filter(lambda x: x.port_group_name == pg_name, self.port_groups)
        )
        if not port_groups:
            msg = (
                f'Port group {pg_name} does not exist in bridge '
                f'network {self.id}'
            )
            LOG.error(msg)
            raise PortGroupException(msg)
        return cast(BridgePortGroup, port_groups.pop())
