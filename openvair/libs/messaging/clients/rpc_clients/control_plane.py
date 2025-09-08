from typing import Dict, List  # noqa: D100

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.control_plane import (
    ControlPlaneServiceABC,
)


class ControlPlaneServiceLayerRPCClient(ControlPlaneServiceABC):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        self.rpc_client = MessagingClient(
            queue_name=RPCQueueNames.ControlPlane.SERVICE_LAYER
        )

    def get_nodes(self) -> List[Dict]:  # noqa: D102
        return []

    def register_node(self, data: Dict) -> Dict:  # noqa: D102, ARG002
        return {}

    def heartbeat(self, data: Dict) -> Dict:  # noqa: D102, ARG002
        return {}

    def choose_node(self, data: Dict) -> Dict:  # noqa: D102, ARG002
        return {}

    def get_cluster_events(self, filters: Dict) -> List[Dict]:  # noqa: D102, ARG002
        return []
