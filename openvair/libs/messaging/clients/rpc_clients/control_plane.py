"""RPC client for the control-plane service.

This module provides a concrete RPC client implementation of
`ControlPlaneServiceABC` that operates on transport-level payloads
(plain `dict[str, object]`). It communicates with the service layer
via `MessagingClient` and queue names defined in `RPCQueueNames`.
"""

from uuid import UUID
from typing import Dict, List, Mapping

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


class ControlPlaneServiceLayerRPCClient(
    ControlPlaneServiceABC[DictObj, DictObj]
):
    """RPC client that talks to the control-plane service layer."""

    def __init__(self) -> None:
        """Initialize the messaging client for the control-plane queue."""
        self.rpc_client = MessagingClient(
            queue_name=RPCQueueNames.ControlPlane.SERVICE_LAYER
        )

    def get_nodes(self) -> List[DictObj]:
        """Fetch nodes from the service layer."""
        nodes: List = self.rpc_client.call(
            ControlPlaneServiceABC.get_nodes.__name__,
        )
        return nodes

    def get_node(self, node_id: UUID) -> DictObj:
        """Fetch a single node by ID."""
        node: Dict = self.rpc_client.call(
            ControlPlaneServiceABC.get_node.__name__,
            data_for_method={'id': node_id},
        )
        return node

    def register_node(self, payload: RegisterNodeServiceCommand) -> DictObj:
        """Register a node in the service layer."""
        result: Dict = self.rpc_client.call(
            ControlPlaneServiceABC.register_node.__name__,
            data_for_method=payload.model_dump(mode='json'),
        )
        return result

    def heartbeat(self, payload: HeartbeatServiceCommand) -> DictObj:
        """Send heartbeat payload to the service layer."""
        result: Dict = self.rpc_client.call(
            ControlPlaneServiceABC.heartbeat.__name__,
            data_for_method=payload.model_dump(mode='json'),
        )
        return result

    def choose_node(self, payload: PlacementRequestServiceCommand) -> DictObj:
        """Request node selection for VM placement."""
        result: Dict = self.rpc_client.call(
            ControlPlaneServiceABC.choose_node.__name__,
            data_for_method=payload.model_dump(mode='json'),
        )
        return result

    def get_cluster_events(
        self,
        filters: Mapping[str, object],
    ) -> List[DictObj]:
        """Fetch cluster events with the given filters."""
        result: List = self.rpc_client.call(
            ControlPlaneServiceABC.get_cluster_events.__name__,
            data_for_method=dict(filters),
        )
        return result
