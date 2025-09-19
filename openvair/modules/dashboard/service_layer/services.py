"""Module for managing dashboard-related operations in the service layer.

This module defines the `DashboardServiceLayerManager` class, which is
responsible for handling operations related to retrieving dashboard data from
nodes. The class uses a unit of work pattern to interact with the Prometheus
data source and provides methods for getting the necessary data.

Classes:
    DashboardServiceLayerManager: Manager class for handling dashboard-related
        operations in the service layer.
"""

from __future__ import annotations

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.dashboard.service_layer import unit_of_work

LOG = get_logger(__name__)


class DashboardServiceLayerManager(BackgroundTasks):
    """Manager class for dashboard-related operations in the service layer.

    This class is responsible for managing operations related to retrieving
    dashboard data from nodes. It uses the PrometheusUnitOfWork to interact
    with the Prometheus data source and provides methods for getting the
    necessary data.
    """

    def __init__(self) -> None:
        """Initialize the DashboardServiceLayerManager.

        This constructor sets up the necessary components for the
        DashboardServiceLayerManager, including initializing the
        unit of work for Prometheus interactions.
        """
        super().__init__()
        self.uow = unit_of_work.PrometheusUnitOfWork

    def get_data(self) -> dict:
        """Retrieve data from the node.

        This method uses the PrometheusUnitOfWork to get the necessary data
        from the node and logs the process.

        Returns:
            Dict: The data retrieved from the node.
        """
        LOG.info('Start getting data from node.')
        with self.uow() as uow:
            data = uow.prometheus.get_data()
        LOG.info('Getting data from node finished successfully.')
        return data
