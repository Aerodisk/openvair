"""Implementation of virtual network management using Open vSwitch.

This module provides an implementation of the network bridge interface using
Open vSwitch (OVS) for managing virtual network bridges and interfaces.

Classes:
    OVSInterface: Implementation of the network bridge interface using OVS.
"""

from typing import Dict, List, Union

from openvair.libs.log import get_logger
from openvair.modules.network.config import NETWORK_CONFIG_MANAGER
from openvair.modules.network.domain.base import Bridge
from openvair.modules.network.domain.bridges.utils.ovs_lib import OVSManager
from openvair.modules.network.domain.bridges.utils.exceptions import (
    OVSManagerException,
)
from openvair.modules.network.domain.bridges.utils.netplan_lib import (
    NetplanManager,
)

LOG = get_logger(__name__)


class OVSInterface(Bridge):
    """Implementation of the network bridge interface using OVS.

    This class provides methods to create and delete network bridges using
    Open vSwitch (OVS) or Netplan, depending on the configuration.

    Attributes:
        ovs_manager (OVSManager): Instance for managing OVS bridges.
        config_manager (Union[OVSManager, NetplanManager]): The configuration
            manager used for managing network configurations.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the OVSInterface instance.

        This constructor initializes the OVS manager and selects the appropriate
        configuration manager based on the network configuration.
        """
        super().__init__(*args, **kwargs)
        self.ovs_manager = OVSManager()
        self.config_manager = self._get_config_manager(NETWORK_CONFIG_MANAGER)

    def _get_config_manager(
        self, config_manager: str
    ) -> Union[OVSManager, NetplanManager]:
        """Retrieve the configuration manager based on the specified type.

        Args:
            config_manager (str): The type of configuration manager ('ovs' or
                'netplan').

        Returns:
            Union[OVSManager, NetplanManager]: An instance of the selected
            configuration manager.
        """
        network_managers = {
            'ovs': OVSManager,
            'netplan': NetplanManager,
        }
        config_manager_class = network_managers.get(config_manager)
        return config_manager_class()

    def create(self, data: Dict) -> None:
        """Create a new interface bridge.

        This method creates a new network bridge using the selected
        configuration manager and applies the configuration.

        Args:
            data (Dict): Data about the new network bridge.
        """
        try:
            self._create_new_bridge()
            self.config_manager.create_configuration(data)

        # TODO: Catch specific exception(s)
        except OVSManagerException as error:
            LOG.error(f'Failed to create interface bridge: {error}')
            self._rollback_on_failure()
            raise

    def delete(self) -> None:
        """Delete a network bridge.

        This method deletes an existing OVS bridge and its configuration using
        the selected configuration manager.
        """
        self.ovs_manager.delete_bridge(self.name)
        self.config_manager.delete_configuration(self.name)

    def get_bridges_list(self) -> List:
        """Retrieve the list of network bridges.

        Returns:
            List: A list of network bridges.
        """
        LOG.info('Start getting the list of bridges')
        bridges_list = self.ovs_manager.get_bridges_list()
        LOG.info('Finished getting the list of bridges')
        return bridges_list

    def _create_new_bridge(self) -> None:
        """Create a new OVS bridge.

        This method initializes the creation of a new OVS bridge.
        """
        LOG.info('Start creating a new OVS bridge')
        self.ovs_manager.create_bridge(self.name)
        LOG.info('Successfully created a new OVS bridge')

    def _rollback_on_failure(self) -> None:
        """Rollback changes in case of failure.

        This method deletes the OVS bridge and its configuration if the bridge
        creation process fails.
        """
        LOG.info('Rolling back changes due to failure')
        self.ovs_manager.delete_bridge(self.name)
        self.config_manager.delete_configuration(self.name)
