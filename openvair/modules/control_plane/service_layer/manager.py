"""Service-layer process bootstrap for the control-plane module.

This module wires the `ControlPlaneServiceLayerManager` into a `MessagingServer`
and starts the RPC server bound to the control-plane queue. It serves as the
runtime entrypoint for the service-layer process.
"""

from openvair.libs.log import get_logger
from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.modules.control_plane.service_layer.services import (
    ControlPlaneServiceLayerManager,
)

LOG = get_logger('service-layer-manager')


if __name__ == '__main__':
    # Instantiate the service class (manager) and start the RPC server.
    service = ControlPlaneServiceLayerManager
    server = MessagingServer(
        queue_name=RPCQueueNames.ControlPlane.SERVICE_LAYER,
        manager=service,
    )
    server.start()
