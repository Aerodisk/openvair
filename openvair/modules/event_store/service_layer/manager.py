"""Some description"""

from openvair.libs.log import get_logger
from openvair.modules.event_store.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.event_store.service_layer.services import (
    EventstoreServiceLayerManager,
)

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')

    service = EventstoreServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
