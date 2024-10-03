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
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.volume.adapters import orm
from openvair.modules.event_store.adapters import orm as event_orm
from openvair.modules.volume.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    orm.start_mappers()
    event_orm.start_mappers()
    LOG.info('Starting RPCServer for consuming')
    service = services.VolumeServiceLayerManager
    service.start(block=False)
    Protocol(server=True)(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
