"""CRUD operations for managing virtual networks.

This module defines a class for performing CRUD operations on virtual networks,
interacting with the service layer to create, retrieve, update, and delete
virtual network resources.

Classes:
    - VirtualNetworkCrud: Provides methods for managing virtual networks,
        including creating, retrieving, updating, and deleting networks and
        their associated port groups.
"""

from uuid import UUID
from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.virtual_network.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.virtual_network.entrypoints import schemas
from openvair.modules.virtual_network.service_layer.services import (
    VirtualNetworkServiceLayerManager,
)

LOG = get_logger(__name__)


class VirtualNetworkCrud:
    """This class provides CRUD operations for managing virtual networks.

    Attributes:
        service_layer_rpc (RabbitRPCClient): An instance of RabbitRPCClient for
            communication with the service layer.
    """

    def __init__(self) -> None:
        """Initializes the VirtualNetworkCrud class."""
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_virtual_networks(self) -> Dict:
        """Retrieves all virtual networks from the service layer.

        Returns:
            Dict: A dictionary containing information about all virtual
                networks.
        """
        LOG.info('Call service layer on getting virtual networks...')

        result: Dict = self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.get_all_virtual_networks.__name__,
            data_for_method={},
        )

        LOG.info('Call service layer on getting virtual networks complete.')
        return result

    def get_virtual_network_by_id(self, vn_id: UUID) -> Dict:
        """Retrieves a virtual network by its ID from the service layer.

        Args:
            vn_id (UUID): The ID of the virtual network to retrieve.

        Returns:
            Dict: A dictionary containing information about the virtual network.
        """
        LOG.info(f'Call service layer on getting virtual networks: {vn_id}...')

        result: Dict = self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.get_virtual_network_by_id.__name__,
            data_for_method={'id': str(vn_id)},
        )

        LOG.info('Call service layer on getting virtual network complete.')
        return result

    def get_virtual_network_by_name(self, vn_name: str) -> Dict:
        """Retrieves a virtual network by its name from the service layer.

        Args:
            vn_name (str): The name of the virtual network to retrieve.

        Returns:
            Dict: A dictionary containing information about the virtual network.
        """
        LOG.info(f'Call service layer on getting virtual network: {vn_name}...')

        result: Dict = self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.get_virtual_network_by_name.__name__,
            data_for_method={'virtual_network_name': vn_name},
        )

        LOG.info('Call service layer on getting virtual network complete.')
        return result

    def create_virtual_network(
        self,
        vn_info: schemas.VirtualNetwork,
        user_info: Dict,
    ) -> Dict:
        """Creates a new virtual network in the service layer.

        Args:
            vn_info (schemas.VirtualNetwork): The data representing the virtual
                network.
            user_info (Dict): The user information.

        Returns:
            Dict: A dictionary containing information about the newly
            created virtual network.
        """
        LOG.info('Call service layer on creating virtual network...')

        service_data = vn_info.dict()
        service_data['user_info'] = user_info

        result: Dict = self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.create_virtual_network.__name__,
            data_for_method=service_data,
            priority=8,
        )

        LOG.info('Call service layer on creating virtual network complete')
        return result

    def delete_virtual_network(
        self,
        vn_id: UUID,
        user_info: Dict,
    ) -> None:
        """Deletes a virtual network by its ID in the service layer.

        Args:
            vn_id (str): The ID of the virtual network to delete.
            user_info (Dict): The user information.
        """
        LOG.info(f'Call service layer on deleting virtual network: {vn_id}...')

        service_data: Dict = {'virtual_network_id': str(vn_id)}
        service_data['user_info'] = user_info
        self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.delete_virtual_network.__name__,
            data_for_method=service_data,
            priority=8,
        )

        LOG.info('Call service layer on deleting virtual network complete')

    def turn_on_virtual_network(self, vn_id: str) -> None:
        """Turns on a virtual network by its ID in the service layer.

        Args:
            vn_id (str): The ID of the virtual network to turn on.
        """
        LOG.info(f'Call service layer for turn on virtual network: {vn_id}...')

        self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.turn_on_virtual_network.__name__,
            data_for_method={'virtual_network_id': vn_id},
            priority=8,
        )

        LOG.info('Call service layer for turn on virtual network complete')

    def turn_off_virtual_network(self, vn_id: str) -> None:
        """Turns off a virtual network by its ID in the service layer.

        Args:
            vn_id (str): The ID of the virtual network to turn off.
        """
        LOG.info(f'Call service layer for turn off virtual network: {vn_id}...')

        self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.turn_off_virtual_network.__name__,
            data_for_method={'virtual_network_id': vn_id},
            priority=8,
        )

        LOG.info('Call service layer for turn off virtual network complete')

    def add_port_group(
        self,
        vn_id: str,
        port_group: schemas.PortGroup,
        user_info: Dict,
    ) -> Dict:
        """Adds a port group to a virtual network in the service layer.

        Args:
            vn_id (str): The ID of the virtual network to which the port group
                will be added.
            port_group (schemas.PortGroup): The port group data to be added.
            user_info (Dict): The user information.

        Returns:
            Dict: A dictionary containing information about the virtual network
                after adding the port group.
        """
        LOG.info('Call service layer on adding port group...')

        service_data = {
            'vn_id': vn_id,
            'port_group_info': port_group.dict(),
        }
        service_data['user_info'] = user_info
        result: Dict = self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.add_port_group.__name__,
            data_for_method=service_data,
        )

        LOG.info('Call service layer on adding port group complete')
        return result

    def delete_port_group(
        self,
        vn_id: str,
        port_group_name: str,
        user_info: Dict,
    ) -> None:
        """Deletes a port group from a virtual network in the service layer.

        Args:
            vn_id (str): The ID of the virtual network from which the port
                group will be deleted.
            port_group_name (str): The name of the port group to delete.
            user_info (Dict): The user information.
        """
        LOG.info('Call service layer on deleting port group...')

        service_data: Dict = {
            'virtual_network_id': vn_id,
            'port_group_name': port_group_name,
        }
        service_data['user_info'] = user_info
        self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.delete_port_group.__name__,
            data_for_method=service_data,
        )

        LOG.info('Call service layer on deleting port group complete')

    def add_tag_to_trunk_port_group(
        self, vn_id: str, pg_name: str, tag_id: str, user_info: Dict
    ) -> Dict:
        """Adds a tag to a trunk port group in a virtual network.

        Args:
            vn_id (str): The ID of the virtual network.
            pg_name (str): The name of the port group.
            tag_id (str): The tag ID to be added to the port group.
            user_info (Dict): The user information.

        Returns:
            Dict: A dictionary containing information about the port group after
                adding the tag.
        """
        LOG.info('Call service layer on adding tag to trunk port group...')

        service_data: Dict = {
            'vn_id': vn_id,
            'pg_name': pg_name,
            'tag': tag_id,
        }
        service_data['user_info'] = user_info
        result: Dict = self.service_layer_rpc.call(
            VirtualNetworkServiceLayerManager.add_tag_to_port_group.__name__,
            data_for_method=service_data,
        )

        LOG.info(
            'Call service layer on adding tag to trunk port group complete'
        )
        return result
