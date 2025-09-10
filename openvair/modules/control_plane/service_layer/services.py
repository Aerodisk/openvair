from typing import Dict, List, Mapping  # noqa: D100

from openvair.libs.messaging.rpc.decorators import rpc_io
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)
from openvair.modules.control_plane.adapters.dto.models import (
    ApiNodeModelDTO,
    ClusterEventModelDTO,
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


class ControlPlaneServiceLayerManager(  # noqa: D101
    ControlPlaneServiceABC[ApiNodeModelDTO, ClusterEventModelDTO]
):
    def get_nodes(self) -> List[ApiNodeModelDTO]:  # noqa: D102
        return []

    @rpc_io()
    def get_node(self, node_id: str) -> ApiNodeModelDTO:  # noqa: ARG002, D102
        return ApiNodeModelDTO.model_validate({})

    @rpc_io()
    def register_node(  # noqa: D102
        self,
        payload: RegisterNodeServiceCommand,  # noqa: ARG002
    ) -> ApiNodeModelDTO:
        return ApiNodeModelDTO.model_validate({})

    @rpc_io()
    def heartbeat(  # noqa: D102
        self,
        payload: HeartbeatServiceCommand,  # noqa: ARG002
    ) -> Dict[str, object]:
        return {}

    @rpc_io()
    def choose_node(  # noqa: D102
        self,
        payload: PlacementRequestServiceCommand,  # noqa: ARG002
    ) -> Dict[str, object]:
        return {}

    @rpc_io()
    def get_cluster_events(  # noqa: D102
        self,
        filters: Mapping[str, object],  # noqa: ARG002
    ) -> List[ClusterEventModelDTO]:
        return []
