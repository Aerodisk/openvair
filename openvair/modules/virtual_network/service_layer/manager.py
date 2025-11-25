"""Manager module for virtual network operations in the service layer.

This module defines the `VirtualNetworkServiceLayerManager` class, responsible
for managing virtual network operations at the service layer. The class
coordinates between the service layer, domain layer, and the database.

Classes:
    - VirtualNetworkServiceLayerManager: Manages virtual network operations,
        including creating, retrieving, updating, and deleting virtual networks
        and their port groups.
"""

from openvair.libs.log import get_logger
from openvair.modules.virtual_network.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.virtual_network.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    service = services.VirtualNetworkServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
