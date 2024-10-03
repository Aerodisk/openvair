"""Manager module for the notification service layer.

This module is responsible for initializing and starting the RPC server for
the notification service layer. It sets up the necessary components, such as
mappers and services, and listens for incoming requests.

Classes:
    - None (Script only)
"""

from openvair.libs.log import get_logger
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.notification.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.notification.adapters import orm
from openvair.modules.notification.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    orm.start_mappers()
    LOG.info('Starting RPCServer for consuming')
    service = services.NotificationServiceLayerManager
    service.start(block=False)
    Protocol(server=True)(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
