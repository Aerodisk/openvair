"""Netplan-based network bridge management.

This module provides an implementation of the network bridge interface using
Netplan for managing network configurations.

Classes:
    NetplanInterface: Netplan-based implementation of the network bridge
        interface.
"""

import json
from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.network.domain.base import Bridge, VirshNetwork
from openvair.modules.network.domain.bridges.utils.netplan_lib import (
    NetplanManager,
)

LOG = get_logger(__name__)


class NetplanInterface(Bridge):
    """Netplan-based implementation of the network bridge interface.

    This class provides methods to create and delete network bridges using
    Netplan for configuration management.

    Attributes:
        virsh_network (VirshNetwork): Instance for managing virsh network.
        netplan_manager (NetplanManager): Instance for managing Netplan
            configurations.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the NetplanInterface instance.

        This constructor initializes the Netplan manager and the Virsh network
        manager for handling network bridge configurations.
        """
        super(NetplanInterface, self).__init__(*args, **kwargs)
        self.virsh_network = VirshNetwork()
        self.netplan_manager = NetplanManager()

    def create(self, data: Dict) -> None:
        """Create a new interface bridge.

        This method creates a new network bridge based on the provided data
        and applies the configuration using Netplan.

        Args:
            data (Dict): Data about the new network bridge.
        """
        yaml_data = self.netplan_manager.create_yaml_config_file(data)
        self.netplan_manager.write_yaml_file(yaml_data)
        self.netplan_manager.apply(self.name)
        self.virsh_network.net_define(
            {'mode': data['type'], 'interface': data['name']}
        )

    def delete(self) -> None:
        """Delete a network bridge.

        This method deletes an existing network bridge configuration using
        Netplan and undefines the associated Virsh network.
        """
        self.netplan_manager.delete_configuration(self.name)
        self.virsh_network.net_undefine(f'{self.type}_network_{self.name}')

    def get_bridges_list(self) -> Dict:
        """Retrieve the list of network bridges.

        Returns:
            Dict: The list of network bridges.
        """
        # TODO: Handle potential errors.
        bridges_data, _ = execute('ip -j link show type bridge')
        return json.loads(bridges_data)
