from typing import Dict, List, Mapping  # noqa: D100

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)
from openvair.libs.messaging.service_interfaces.control_plane import (
    ControlPlaneServiceABC,
)

DictObj = Dict[str, object]


class ControlPlaneServiceLayerRPCClient(  # noqa: D101
    ControlPlaneServiceABC[DictObj, DictObj]
):
    def __init__(self) -> None:  # noqa: D107
        self.rpc_client = MessagingClient(
            queue_name=RPCQueueNames.ControlPlane.SERVICE_LAYER
        )

    def get_nodes(self) -> List[DictObj]:  # noqa: D102
        return []

    def get_node(self, node_id: str) -> DictObj:  # noqa: ARG002, D102
        return {}

    def register_node(self, payload: RegisterNodeServiceCommand) -> DictObj:  # noqa: ARG002, D102
        return {}

    def heartbeat(self, payload: HeartbeatServiceCommand) -> DictObj:  # noqa: ARG002, D102
        return {}

    def choose_node(self, payload: PlacementRequestServiceCommand) -> DictObj:  # noqa: ARG002, D102
        return {}

    def get_cluster_events(  # noqa: D102
        self,
        filters: Mapping[str, object],  # noqa: ARG002
    ) -> List[DictObj]:
        return []
