"""Service layer manager for handling backup-related messaging.

This script serves as the entry point for managing backup operations
via an RPC interface. It initializes a messaging server using the
`BackupServiceLayerManager` to process backup-related tasks.

The script is designed to run as a systemd service. During installation,
a setup script automatically registers and starts the corresponding
`.service` file located at:
    /opt/aero/openvair/openvair/modules/backup/service_layer/backup-service-layer.service

Usage:
    Manual management of the service:
        To start the service:
            sudo systemctl start backup-service-layer.service
        To stop the service:
            sudo systemctl stop backup-service-layer.service
        To check the status:
            sudo systemctl status backup-service-layer.service

    Logs can be reviewed via:
        journalctl -u backup-service-layer.service
"""

from openvair.libs.log import get_logger
from openvair.modules.backup.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.backup.service_layer.services import (
    BackupServiceLayerManager,
)

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    LOG.info('Starting RPCServer for consuming')
    service = BackupServiceLayerManager
    service.start(block=False)
    server = MessagingServer(
        queue_name=API_SERVICE_LAYER_QUEUE_NAME,
        manager=service,
    )
    server.start()
