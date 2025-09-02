from services import ControlPlaneServiceLayerManager  # noqa: D100

from openvair.libs.log import get_logger
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    service = ControlPlaneServiceLayerManager
    server = MessagingServer(
        queue_name='control_plane-service-layer-queue',
        manager=service,
    )
    server.start()
