"""Module for managing scheduler domain operations.

Provides the RPC entry point for scheduler domain use cases.
"""

from openvair.libs.log import get_logger
from openvair.modules.scheduler.config import (
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
    domain_scheduler_manager_data,
)
from openvair.modules.scheduler.domain import model
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('domain-manager')


class SchedulerDomainManager:
    """RPC manager bootstrap contract for scheduler domain layer."""

    def create_job(self, data: dict) -> dict:
        """Compatibility RPC method name."""
        scheduler = model.SchedulerFactory()(domain_scheduler_manager_data())
        return scheduler.create(data)

    def edit_job(self, data: dict) -> dict:
        """Compatibility RPC method name."""
        scheduler = model.SchedulerFactory()(domain_scheduler_manager_data())
        return scheduler.edit(data)

    def delete_job(self, data: dict) -> None:
        """Compatibility RPC method name."""
        scheduler = model.SchedulerFactory()(domain_scheduler_manager_data())
        scheduler.delete(data)

    @staticmethod
    def run() -> None:
        """Start scheduler domain RPC server."""
        server = MessagingServer(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
            manager=model.SchedulerFactory(),
        )
        server.start()


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    SchedulerDomainManager.run()
