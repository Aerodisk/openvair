"""Module for managing storage domain services.

This module defines the entry point for the storage domain service layer. It
sets up and starts an RPC server to handle storage-related requests using the
storage factory defined in the model.

Functions:
    main: The main entry point to start the RPC server.
"""

from openvair.libs.log import get_logger
from openvair.modules.storage.config import SERVICE_LAYER_DOMAIN_QUEUE_NAME
from openvair.modules.storage.domain import model
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('domain-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    server = MessagingServer(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=model.StorageFactory(),
    )
    server.start()
