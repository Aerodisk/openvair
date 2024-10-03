"""Module for managing the volume domain layer.

This module provides the entry point for managing the volume domain layer,
including starting the RPC server for handling requests related to volume
operations.

The module also sets up the logging and protocol configurations.

Entry Point:
    This module should be run as the main module to start the RPC server.
"""

from openvair.libs.log import get_logger
from openvair.modules.volume.config import SERVICE_LAYER_DOMAIN_QUEUE_NAME
from openvair.modules.volume.domain import model
from openvair.libs.messaging.protocol import Protocol

LOG = get_logger('domain-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    Protocol(server=True)(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=model.VolumeFactory(),
    )
