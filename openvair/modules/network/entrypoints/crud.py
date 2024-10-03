"""CRUD operations for managing network interfaces and bridges.

This module provides a class for performing CRUD operations related to
network interfaces and bridges, including retrieving interface data, creating
and deleting bridges, and controlling interfaces.

Classes:
    InterfaceCrud: A class for managing network interface and bridge CRUD
        operations.
"""

from typing import Dict, List

from openvair.libs.log import get_logger
from openvair.libs.client.config import get_os_type
from openvair.modules.tools.utils import validate_objects
from openvair.modules.network.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.network.entrypoints import schemas
from openvair.modules.network.service_layer import services

LOG = get_logger(__name__)


class InterfaceCrud:
    """A class for managing network interface and bridge CRUD operations.

    This class provides methods for retrieving, creating, updating, and
    deleting network interfaces and bridges through interactions with the
    service layer.

    Attributes:
        service_layer_rpc (Protocol): RPC protocol for communicating with the
            service layer.
    """

    def __init__(self):
        """Initialize the InterfaceCrud instance.

        This constructor sets up the RPC protocol for communicating with the
        service layer.
        """
        self.service_layer_rpc = Protocol(client=True)(
            API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_interfaces(
        self,
        *,
        is_need_filter: bool = False,
    ) -> List[schemas.Interface]:
        """Retrieve all network interfaces.

        This method calls the service layer to retrieve all network interfaces,
        optionally applying a filter based on the provided flag.

        Args:
            is_need_filter (Optional[bool], optional): Flag indicating whether
                to apply filtering on interfaces. Defaults to False.

        Returns:
            List[schemas.Interface]: A list of interfaces retrieved from the
                service layer.
        """
        LOG.info('Call service layer on getting all interfaces.')
        data = {'is_need_filter': is_need_filter}
        result = self.service_layer_rpc.call(
            services.NetworkServiceLayerManager.get_all_interfaces.__name__,
            data_for_method=data,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return validate_objects(result, schemas.Interface)

    def get_interface(self, iface_id: str) -> Dict:
        """Retrieve a specific network interface.

        This method calls the service layer to retrieve data for a specific
        network interface identified by its ID.

        Args:
            iface_id (str): The UUID of the network interface to retrieve.

        Returns:
            Dict: A dictionary containing data about the specified interface.
        """
        LOG.info('Call service layer on getting interface.')
        result = self.service_layer_rpc.call(
            services.NetworkServiceLayerManager.get_interface.__name__,
            data_for_method={'iface_id': iface_id},
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def get_bridges_list(self) -> List[str]:
        """Retrieve the list of network bridges.

        This method calls the service layer to retrieve a list of all network
        bridges.

        Returns:
            List[str]: A list of network bridges.
        """
        LOG.info('Getting the list of network bridges')
        result = self.service_layer_rpc.call(
            services.NetworkServiceLayerManager.get_bridges_list.__name__,
            data_for_method={},
        )
        LOG.info('Response from service layer : %s.' % result)
        return result

    def create_bridge(self, data: Dict, user_info: Dict) -> Dict:
        """Create a new network bridge.

        This method calls the service layer to create a new network bridge
        based on the provided data and user information.

        Args:
            data (Dict): A dictionary containing information about the bridge
                to be created.
            user_info (Dict): A dictionary containing user information.

        Returns:
            Dict: A dictionary containing the result of the bridge creation.
        """
        LOG.info('Call service layer on create network bridge.')
        os_type_interface = get_os_type()
        data.update(
            {
                'user_info': user_info,
                'inf_type': os_type_interface,
            }
        )
        result = self.service_layer_rpc.call(
            services.NetworkServiceLayerManager.create_bridge.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer : %s.' % result)
        return result

    def delete_bridge(self, data: List, user_info: Dict) -> List:
        """Delete a network bridge.

        This method calls the service layer to delete a network bridge based
        on the provided data and user information.

        Args:
            data (List): A list of dictionaries containing information about
                the bridges to be deleted.
            user_info (Dict): A dictionary containing user information.

        Returns:
            List: A list of responses from the service layer for each deleted
                bridge.
        """
        LOG.info('Call service layer on delete network bridge.')
        os_type_interface = get_os_type()
        result = []

        for iface in data:
            iface.update(
                {
                    'user_info': user_info,
                    'inf_type': os_type_interface,
                }
            )
            rpc_result = self.service_layer_rpc.call(
                services.NetworkServiceLayerManager.delete_bridge.__name__,
                data_for_method=iface,
            )
            result.append(rpc_result)
            LOG.debug('Response from service layer : %s.' % result)
        return result

    def turn_on_interface(self, name: str) -> Dict:
        """Turn on the specified virtual network interface.

        This method calls the service layer to turn on a virtual network
        interface identified by its name. It sends the request to the network
        service layer manager with a specified priority.

        Args:
            name (str): The name of the virtual network interface to be
                turned on.

        Returns:
            Dict: A dictionary containing the result of the turn-on operation.
        """
        LOG.info(f'Call service layer for turn on virtual network: {name}...')

        result = self.service_layer_rpc.call(
            services.NetworkServiceLayerManager.turn_on.__name__,
            data_for_method={'name': name},
            priority=8,
        )

        LOG.info('Call service layer for turn on virtual network complete')
        return result

    def turn_off_interface(self, name: str) -> Dict:
        """Turn off the specified virtual network interface.

        This method calls the service layer to turn off a virtual network
        interface identified by its name. It sends the request to the network
        service layer manager with a specified priority.

        Args:
            name (str): The name of the virtual network interface to be
                turned off.

        Returns:
            Dict: A dictionary containing the result of the turn-off operation.
        """
        LOG.info(f'Call service layer for turn off virtual network: {name}...')

        result = self.service_layer_rpc.call(
            services.NetworkServiceLayerManager.turn_off.__name__,
            data_for_method={'name': name},
            priority=8,
        )

        LOG.info('Call service layer for turn off virtual network complete')
        return result
