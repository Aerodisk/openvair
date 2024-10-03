"""Service layer manager for the image service.

This module is responsible for initializing and starting the RPC server for
the image service layer. It sets up the necessary database mappings and
protocols for handling image-related operations, and it ensures that the
service layer is ready to process incoming requests.

Usage:
    Run this script to start the service layer manager for the image service.
"""

from openvair.libs.log import get_logger
from openvair.modules.image.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.image.adapters import orm
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.image.service_layer import services
from openvair.modules.event_store.adapters import orm as event_orm

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    orm.start_mappers()
    event_orm.start_mappers()
    LOG.info('Starting RPCServer for consuming')
    service = services.ImageServiceLayerManager
    service.start(block=False)
    Protocol(server=True)(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
