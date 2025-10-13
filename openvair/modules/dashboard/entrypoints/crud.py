"""Module for providing CRUD operations for the Dashboard.

This module defines the `DashboardCrud` class, which is responsible for
handling CRUD (Create, Read, Update, Delete) operations related to the
Dashboard. The class uses the `Protocol` class from the
`openvair.libs.messaging.protocol` module to communicate with the service layer
and perform the requested operations.

The module includes methods for retrieving data from the dashboard.

Classes:
    DashboardCrud: Provides CRUD operations for the Dashboard.
"""


from openvair.libs.log import get_logger
from openvair.modules.dashboard.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.dashboard.service_layer import services

LOG = get_logger(__name__)


class DashboardCrud:
    """Class providing CRUD operations for the Dashboard.

    This class is responsible for handling CRUD operations related to the
    Dashboard by communicating with the service layer using the `Protocol` class

    Attributes:
        service_layer_rpc (RabbitRPCClient): RPC client for communicating with
            the Dashboard Service Layer.
    """

    def __init__(self) -> None:
        """Initialize a DashboardCrud object.

        The constructor sets up the connection to the service layer queue
        using the `Protocol` class.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_data(self) -> dict:
        """Get data for the dashboard.

        Returns:
            Dict: The result of the get_data operation.
        """
        LOG.info('Call service layer on getting node data.')
        data: dict = self.service_layer_rpc.call(
            services.DashboardServiceLayerManager.get_data.__name__, {}
        )
        LOG.info(f'Response from service layer: {data}.')
        return data
