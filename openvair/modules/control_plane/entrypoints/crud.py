from typing import Dict, List  # noqa: D100

from openvair.libs.log import get_logger
from openvair.libs.messaging.clients.rpc_clients.control_plane import (
    ControlPlaneServiceLayerRPCClient,
)
from openvair.modules.control_plane.entrypoints.schemas.requests import (
    HeartbeatRequest,
    VmPlacementRequest,
    NodeRegisterRequest,
)

LOG = get_logger(__name__)


class ControlPlaneCrud:  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        self.service_layer_rpc_client = ControlPlaneServiceLayerRPCClient()

    def get_nodes(self) -> List[Dict]:  # noqa: D102
        return []

    def get_node(self) -> Dict:  # noqa: D102
        return {}

    def register_node(self, request: NodeRegisterRequest) -> Dict:  # noqa: D102, ARG002
        return {}

    def heartbeat(self, request: HeartbeatRequest) -> Dict:  # noqa: D102, ARG002
        return {}

    def choose_node(self, request: VmPlacementRequest) -> Dict:  # noqa: D102, ARG002
        return {}

    def get_cluster_events(self, filters: Dict) -> List[Dict]:  # noqa: D102, ARG002
        return []
