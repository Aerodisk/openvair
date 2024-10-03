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
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.event_store.adapters import orm as event_orm
from openvair.modules.virtual_network.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.virtual_network.adapters import orm
from openvair.modules.virtual_network.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    orm.start_mappers()
    event_orm.start_mappers()
    LOG.info('Starting RPCServer for consuming')
    service = services.VirtualNetworkServiceLayerManager
    service.start(block=False)
    Protocol(server=True)(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
