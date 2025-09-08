from typing import Dict, List  # noqa: D100

from pydantic import validate_call

from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)
from openvair.libs.messaging.service_interfaces.control_plane import (
    ControlPlaneServiceABC,
)


def call_vm_on_node(  # noqa: D103
    target_node: str,
    method: str,
    data: dict,
    timeout: float = 20.0,
) -> Dict:
    queue = f'vm.req.{target_node}'
    client = MessagingClient(queue_name=queue)
    resp: Dict = client.call(
        method_name=method,
        data_for_method=data,
        time_limit=timeout,
    )
    return resp


class ControlPlaneServiceLayerManager(ControlPlaneServiceABC):  # noqa: D101
    def get_nodes(self) -> List[Dict]:  # noqa: D102
        return []

    @validate_call
    def register_node(self, payload: RegisterNodeServiceCommand) -> Dict:  # noqa: D102, ARG002
        return {}

    @validate_call
    def heartbeat(self, payload: HeartbeatServiceCommand) -> Dict:  # noqa: ARG002, D102
        return {}

    @validate_call
    def choose_node(self, payload: PlacementRequestServiceCommand) -> Dict:  # noqa: D102, ARG002
        return {}

    @validate_call
    def get_cluster_events(self, filters: Dict) -> List[Dict]:  # noqa: D102, ARG002
        return []
