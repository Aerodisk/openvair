"""Module for providing CRUD operations on block device interfaces.

This module defines the `InterfaceCrud` class, which is responsible for
handling CRUD (Create, Read, Update, Delete) operations on block device
interfaces, such as iSCSI and Fibre Channel. The class uses the `Protocol`
class from the `openvair.libs.messaging.protocol` module to communicate with
the service layer and perform the requested operations.

The module includes methods for getting all iSCSI sessions, getting the current
host IQN, logging in and out of iSCSI block devices, and performing a LIP
(Loop Initialization Procedure) scan on Fibre Channel host adapters.

Classes:
    InterfaceCrud: Provides CRUD operations on block device interfaces.
"""

from typing import Dict, List, cast

from openvair.libs.log import get_logger
from openvair.modules.block_device.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.block_device.service_layer import services

LOG = get_logger(__name__)


class InterfaceCrud:
    """Class providing CRUD operations on block device interfaces.

    This class is responsible for handling CRUD operations on block device
    interfaces, such as iSCSI and Fibre Channel, by communicating with the
    service layer using the `Protocol` class.

    Attributes:
        service_layer_rpc (RabbitRPCClient): RPC client for communicating with
            the block device service layer.
    """

    def __init__(self) -> None:
        """Initialize an InterfaceCrud object.

        The constructor sets up the connection to the service layer queue
        using the `Protocol` class.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_sessions(self) -> List:
        """Get all iSCSI sessions.

        Returns:
            Dict: The result of the get_all_sessions operation.
        """
        LOG.info('Start getting all ISCSI sessions')
        result = self.service_layer_rpc.call(
            services.BlockDevicesServiceLayerManager.get_all_sessions.__name__,
            data_for_method={},
        )
        LOG.info('Complete getting all ISCSI sessions')
        return cast('List', result)

    def get_host_iqn(self) -> Dict:
        """Get the current host IQN.

        Returns:
            Dict: The result of the get_host_iqn operation.
        """
        LOG.info('Start getting current host IQN')
        result: Dict = self.service_layer_rpc.call(
            services.BlockDevicesServiceLayerManager.get_host_iqn.__name__
        )
        LOG.info('Complete getting current host IQN')
        return result

    def login(self, data: Dict, user_data: Dict) -> Dict:
        """Log in to an iSCSI block device.

        Args:
            data (Dict): The data required for the login operation.
            user_data (Dict): Additional user data to be included in the
                request.

        Returns:
            Dict: The result of the login operation.
        """
        LOG.info(f'Login to the ISCSI block device: {data}')
        data.update({'user_data': user_data})
        result: Dict = self.service_layer_rpc.call(
            services.BlockDevicesServiceLayerManager.login.__name__,
            data_for_method=data,
        )
        LOG.info('Successfully logged in with ISCSI block device')
        return result

    def logout(self, data: Dict, user_data: Dict) -> Dict:
        """Log out of an iSCSI block device.

        Args:
            data (Dict): The data required for the logout operation.
            user_data (Dict): Additional user data to be included in the
                request.

        Returns:
            Dict: The result of the logout operation.
        """
        LOG.info('Logging out with ISCSI block device')
        data.update({'user_data': user_data})
        result: Dict = self.service_layer_rpc.call(
            services.BlockDevicesServiceLayerManager.logout.__name__,
            data_for_method=data,
        )
        LOG.info('Successfully logged out from the ISCSI block device')
        return result

    def lip_scan(self) -> str:
        """Perform a LIP scan on Fibre Channel host adapters.

        LIP - Loop Initialization Procedure
        Returns:
            Dict: The result of the LIP scan operation.
        """
        LOG.info('Crud request to scan for FC host adapters')
        result: str = self.service_layer_rpc.call(
            services.BlockDevicesServiceLayerManager.lip_scan.__name__,
            data_for_method={},
        )
        LOG.info('Successfully scanned')
        return str(result)
