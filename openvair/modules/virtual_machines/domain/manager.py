"""Module for managing the RPC server for virtual machines.

This module starts an RPC server that listens for messages related to
virtual machine operations. It uses the Protocol class to handle the
communication and delegates the management of virtual machines to a
driver factory.

Classes:
    VMDriverFactory: Factory class for creating VM drivers.

Functions:
    main: Starts the RPC server for virtual machine management.
"""

from openvair.libs.log import get_logger
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.virtual_machines.config import (
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.virtual_machines.domain import model

LOG = get_logger('domain-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    server = MessagingServer(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=model.VMDriverFactory(),
    )
    server.start()
