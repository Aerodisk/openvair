"""Manager module for the notification service layer.

This module is responsible for initializing and starting the RPC server for
the notification service layer. It sets up the necessary components, such as
mappers and services, and listens for incoming requests.

Classes:
    - None (Script only)
"""

from openvair.libs.log import get_logger
from openvair.modules.notification.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.notification.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    service = services.NotificationServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
