"""Domain manager for handling notification consumption.

This module starts the RPC server that consumes notifications and delegates
them to the appropriate handlers.
"""

from openvair.libs.log import get_logger
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.notification.config import SERVICE_LAYER_DOMAIN_QUEUE_NAME
from openvair.modules.notification.domain import model

LOG = get_logger('domain-manager')

if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    Protocol(server=True)(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=model.NotificationFactory(),
    )
