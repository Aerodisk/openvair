"""Domain manager for the image service.

This script initializes and starts the RPC server for handling image-related
operations in the domain layer. It listens for incoming requests on the
specified queue and delegates them to the appropriate handlers.

Usage:
    Run this script to start the domain-layer manager.
"""

from openvair.libs.log import get_logger
from openvair.modules.image.config import SERVICE_LAYER_DOMAIN_QUEUE_NAME
from openvair.modules.image.domain import model
from openvair.libs.messaging.protocol import Protocol

LOG = get_logger('domain-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    Protocol(server=True)(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=model.ImageFactory(),
    )
