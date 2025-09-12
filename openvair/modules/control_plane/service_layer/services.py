"""Service-layer implementation for the control-plane module.

This module contains the concrete service implementation that fulfills the
generic control-plane interface with domain DTOs. The `@rpc_io` decorator
validates inputs, optionally validates outputs, and serializes return values
into transport-safe structures at the RPC boundary.
"""

from uuid import UUID
from typing import Dict, List, Mapping

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


def call_vm_on_node(
    target_node: str,
    method: str,
    data: dict,
    timeout: float = 20.0,
) -> Dict:
    """Call a VM-related RPC on a specific node queue.

    Args:
        target_node: Node identifier used to build the queue name.
        method: Remote method name to invoke.
        data: Payload sent to the remote method.
        timeout: Time limit for the RPC call, in seconds.

    Returns:
        Dict: Transport-safe response payload.
    """
    queue = f'vm.req.{target_node}'
    client = MessagingClient(queue_name=queue)
    resp: Dict = client.call(
        method_name=method,
        data_for_method=data,
        time_limit=timeout,
    )
    return resp


class ControlPlaneServiceLayerManager(
    ControlPlaneServiceABC[ApiNodeModelDTO, ClusterEventModelDTO]
):
    """Concrete service-layer manager returning domain DTOs."""

    def get_nodes(self) -> List[ApiNodeModelDTO]:
        """Return the list of nodes as DTOs."""
        return []

    @rpc_io()
    def get_node(self, node_id: UUID) -> ApiNodeModelDTO:  # noqa: ARG002
        """Return a single node as DTO."""
        return ApiNodeModelDTO.model_validate({})

    @rpc_io()
    def register_node(
        self,
        payload: RegisterNodeServiceCommand,  # noqa: ARG002
    ) -> ApiNodeModelDTO:
        """Register a node and return the resulting DTO."""
        return ApiNodeModelDTO.model_validate({})

    @rpc_io()
    def heartbeat(
        self,
        payload: HeartbeatServiceCommand,  # noqa: ARG002
    ) -> Dict[str, object]:
        """Process a heartbeat and return a transport payload."""
        return {}

    @rpc_io()
    def choose_node(
        self,
        payload: PlacementRequestServiceCommand,  # noqa: ARG002
    ) -> Dict[str, object]:
        """Select a node for VM placement and return a transport payload."""
        return {}

    @rpc_io()
    def get_cluster_events(
        self,
        filters: Mapping[str, object],  # noqa: ARG002
    ) -> List[ClusterEventModelDTO]:
        """Return cluster events as DTOs according to the provided filters."""
        return []
