"""Module for managing the service layer of virtual machines.

This module initializes the ORM mappers, starts the service layer manager,
and sets up an RPC server for handling requests related to virtual machine
operations. The service layer manager handles the core business logic for
virtual machine operations and communicates with other components via RPC.

Classes:
    None

Functions:
    main: Initializes the ORM mappers, starts the service layer manager,
        and sets up the RPC server for handling requests.
"""

from openvair.libs.log import get_logger
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.event_store.adapters import orm as event_orm
from openvair.modules.virtual_machines.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
)
from openvair.modules.virtual_machines.adapters import orm
from openvair.modules.virtual_machines.service_layer import services

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    orm.start_mappers()
    event_orm.start_mappers()
    LOG.info('Starting RPCServer for consuming')
    service = services.VMServiceLayerManager
    service.start(block=False)
    Protocol(server=True)(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
