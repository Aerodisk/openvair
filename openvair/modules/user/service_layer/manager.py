"""Service layer manager for the user service.

This module is responsible for initializing and starting the RPC server for
the user service layer. It sets up the necessary database mappings and
protocols for handling user-related operations, and it ensures that the
service layer is ready to process incoming requests.

Usage:
    Run this script to start the service layer manager for the user service.
"""

from openvair.libs.log import get_logger
from openvair.modules.user.config import USER_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.user.service_layer import services
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting User RPCServer for consuming')
    service = services.UserManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=USER_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
