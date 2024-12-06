"""Module providing base classes for virtual networks and port groups.

This module defines the abstract base classes `BasePortGroup` and
`BaseVirtualNetwork`, which are used to represent port groups and virtual
networks, respectively.

Classes:
    - BasePortGroup: Abstract base class for port groups.
    - BaseVirtualNetwork: Abstract base class for virtual networks.
"""

import abc
from typing import Any, Dict, List

from openvair.modules.virtual_network.adapters.virsh_adapter import (
    VirshNetworkAdapter,
)


class BasePortGroup(metaclass=abc.ABCMeta):
    """Abstract base class for port groups.

    Attributes:
        port_group_name (str): The name of the port group.
        is_trunk (str): Indicates if the port group is in trunk mode.
        tags (List[str]): List of tags associated with the port group.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the BasePortGroup instance."""
        self.port_group_name = str(kwargs.pop('port_group_name'))
        self.is_trunk = str(kwargs.pop('is_trunk', 'no'))
        self.tags: List[str] = list(kwargs.pop('tags', []))

    def __eq__(self, other: object) -> bool:
        """Check if two port groups are equal based on their names."""
        if isinstance(other, BasePortGroup):
            return self.port_group_name == other.port_group_name
        return False

    def __hash__(self) -> int:
        """Compute the hash value based on the port group name."""
        return hash(self.port_group_name)

    @abc.abstractmethod
    def add_tag(self, tag: str) -> None:
        """Abstract method to add a tag to the port group."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_tag(self, tag: str) -> None:
        """Abstract method to delete a tag from the port group."""
        raise NotImplementedError

    def as_dict(self) -> Dict[str, Any]:
        """Converts the port group object to a dictionary.

        Returns:
            Dict[str, str]: Dictionary representation of the port group.
        """
        return {
            'port_group_name': self.port_group_name,
            'is_trunk': self.is_trunk,
            'tags': self.tags,
        }


class BaseVirtualNetwork(metaclass=abc.ABCMeta):
    """Abstract base class for virtual networks.

    Attributes:
        id (str): The ID of the virtual network.
        network_name (str): The name of the virtual network.
        forward_mode (str): The forward mode of the virtual network.
        bridge (str): The bridge of the virtual network.
        virtual_port_type (str): The virtual port type of the virtual network.
        port_groups (List[BasePortGroup]): List of port groups associated with
            the virtual network.
        virsh_xml (str): The XML representation of the virtual network.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the BaseVirtualNetwork instance."""
        self.id = str(kwargs.pop('id', ''))
        self.network_name = str(kwargs.pop('network_name', ''))
        self.forward_mode = str(kwargs.pop('forward_mode', 'openvswitch'))
        self.bridge = str(kwargs.pop('bridge', ''))
        self.virtual_port_type = str(
            kwargs.pop('virtual_port_type', 'openvswitch')
        )
        self.port_groups: List[BasePortGroup] = list(
            kwargs.pop('port_groups', [])
        )
        self.virsh_xml = str(kwargs.pop('virsh_xml', ''))
        self.virsh = VirshNetworkAdapter()

    @abc.abstractmethod
    def add_port_group(self, port_group: Dict) -> Dict[str, Any]:
        """Abstract method to add a port group to the virtual network.

        Args:
            port_group (Dict): Information about the port group.

        Returns:
            Dict[str, Any]: Updated network data.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def del_port_group_by_name(self, data: Dict) -> Dict[str, str]:
        """Abstract method to delete a port group from virtual network by name.

        Args:
            data (Dict): Dictopnary woth the name of the port group to delete.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create(self) -> Dict[str, str]:
        """Abstract method to create the virtual network.

        Returns:
            Dict[str, str]: Network data.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self) -> None:
        """Abstract method to delete the virtual network."""
        raise NotImplementedError

    @abc.abstractmethod
    def enable(self) -> str:
        """Abstract method to enable the virtual network.

        Returns:
            str: Network state.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def disable(self) -> str:
        """Abstract method to disable the virtual network.

        Returns:
            str: Network state.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_exist_in_virsh(self) -> bool:
        """Abstract method to check if the virtual network exists in virsh.

        Returns:
            Dict: Network existence information.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_tag_to_port_group(self, data: Dict) -> Dict[str, Dict[str, str]]:
        """Abstract method to add a tag to a port group in the virtual network.

        Args:
            data (Dict): Data containing the tag ID and port group name.

        Returns:
            Dict[str, Dict[str, str]]: Updated network data.
        """
        raise NotImplementedError

    def as_dict(self) -> Dict[str, Any]:
        """Converts the virtual network object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the virtual network.
        """
        return {
            'id': str(self.id),
            'network_name': self.network_name,
            'forward_mode': self.forward_mode,
            'bridge': self.bridge,
            'virtual_port_type': self.virtual_port_type,
            'port_groups': [pg.as_dict() for pg in self.port_groups],
        }
