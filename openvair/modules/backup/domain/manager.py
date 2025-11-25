"""Domain manager for handling backup-related messaging.

This script serves as the entry point for managing backup operations
via an RPC interface. It initializes a messaging server using the
`BackuperFactory` to process backup-related tasks.

The script is designed to run as a systemd service. During installation,
a setup script automatically registers and starts the corresponding
`.service` file located at:
    /opt/aero/openvair/openvair/modules/backup/domain/backup-domain.service

Usage:
    Manual management of the service:
        To start the service:
            sudo systemctl start backup-domain.service
        To stop the service:
            sudo systemctl stop backup-domain.service
        To check the status:
            sudo systemctl status backup-domain.service

    Logs can be reviewed via:
        journalctl -u backup-domain.service
"""

from openvair.libs.log import get_logger
from openvair.modules.backup.config import SERVICE_LAYER_DOMAIN_QUEUE_NAME
from openvair.modules.backup.domain.model import BackuperFactory
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('domain-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    server = MessagingServer(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
        manager=BackuperFactory(),
    )
    server.start()
