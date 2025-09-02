from openvair.rpc_queues import RPCQueueNames  # noqa: D100, I001
from services import ControlPlaneServiceLayerManager

from openvair.libs.log import get_logger
from openvair.libs.messaging.messaging_agents import MessagingServer

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    service = ControlPlaneServiceLayerManager
    server = MessagingServer(
        queue_name=RPCQueueNames.ControlPlane.SERVICE_LAYER,
        manager=service,
    )
    server.start()
