"""Module for initializing the Volume Service Layer Manager.

This module initializes and starts the Volume Service Layer Manager,
which is responsible for handling RPC calls related to volume management
operations such as creating, deleting, and modifying volumes.

The manager interacts with the domain layer and the database through
ORM mappers, and it uses a message queue for handling requests.

This module also starts the RPC server for consuming requests.

Entrypoints:
    The module is intended to be executed as a script to start the
    Volume Service Layer Manager and RPC server.
"""

from openvair.libs.log import get_logger
from openvair.modules.volume.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.volume.service_layer import services
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    service = services.VolumeServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
