"""Service layer manager for handling storage-related operations.

This module serves as the entry point for storage management operations within
the service layer. It coordinates tasks such as creating, retrieving, and
deleting storages, while ensuring proper communication between the API, domain,
and database layers.

Entrypoint:
    The main entry point initializes necessary components, starts the RPC
        server, and begins consuming storage-related requests.
"""

from openvair.libs.log import get_logger
from openvair.modules.storage.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.storage.adapters import orm
from openvair.modules.event_store.adapters import orm as event_orm
from openvair.modules.storage.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    orm.start_mappers()
    event_orm.start_mappers()
    LOG.info('Starting RPCServer for consuming')
    service = services.StorageServiceLayerManager
    service.start(block=False)
    Protocol(server=True)(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
