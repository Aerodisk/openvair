"""Manager for network domain operations.

This module contains the entry point for starting the RPC server that
handles network-related domain operations.

Attributes:
    LOG (Logger): Logger instance for logging events in the module.
"""

from openvair.libs.log import get_logger
from openvair.modules.network.config import SERVICE_LAYER_DOMAIN_QUEUE_NAME
from openvair.modules.network.domain import model
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('domain-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    server = MessagingServer(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=model.InterfaceFactory(),
    )
    server.start()
