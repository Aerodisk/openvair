"""Service layer manager for network operations.

This module starts the service layer manager, which handles network
operations by consuming messages from the specified queue and processing
them using the NetworkServiceLayerManager.

Functions:
    main: Initializes and starts the service layer manager.
"""

from openvair.libs.log import get_logger
from openvair.modules.network.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.network.service_layer import services
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    service = services.NetworkServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
