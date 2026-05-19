"""Module for managing scheduler domain operations.

This module provides the entry point for managing scheduler domain operations.
It creates an RPC server to consume messages related to scheduler management.

#TODO classes

#TODO dependencies
"""

from openvair.libs.log import get_logger
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('domain-manager')

if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    server = MessagingServer(
        # TODO move this to a config
        queue_name='scheduler_service_layer_domain',
        manager=model.SchedulerFactory()
    )
    server.start
