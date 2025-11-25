"""Module for initializing the Dashboard Service Layer Manager.

This module sets up and starts the RPC server for the Dashboard Service Layer
Manager. It configures the logging, initializes the service manager, and starts
the RPC server for consuming requests related to dashboard operations.

The module is intended to be run as a standalone script to initialize the
dashboard service layer manager and make it ready to handle incoming RPC calls.

Classes:
    DashboardServiceLayerManager: Manager class for handling dashboard-related
        operations in the service layer. (imported from services module)
"""

from openvair.libs.log import get_logger
from openvair.modules.dashboard.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.dashboard.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting dashboard RPCServer for consuming')
    service = services.DashboardServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=services.DashboardServiceLayerManager,
    )
    server.start()
