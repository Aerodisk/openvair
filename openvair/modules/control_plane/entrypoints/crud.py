"""CRUD entrypoints for the control-plane module.

This module exposes application-facing methods (e.g., for HTTP handlers or CLI)
and delegates actual work to the control-plane RPC client. All methods operate
with transport-safe dictionaries suitable for serialization.
"""

from uuid import UUID
from typing import Dict, List

from openvair.libs.log import get_logger
from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)
from openvair.libs.messaging.clients.rpc_clients.control_plane import (
    ControlPlaneServiceLayerRPCClient,
)
from openvair.modules.control_plane.entrypoints.schemas.requests import (
    HeartbeatRequest,
    VmPlacementRequest,
    NodeRegisterRequest,
)

LOG = get_logger(__name__)


class ControlPlaneCrud:
    """High-level CRUD adapter that talks to the control-plane RPC client."""

    def __init__(self) -> None:
        """Initialize the underlying RPC client."""
        self.service_layer_rpc_client = ControlPlaneServiceLayerRPCClient()

    def get_nodes(self) -> List[Dict]:
        """Return the list of nodes."""
        return self.service_layer_rpc_client.get_nodes()

    def get_node(self, node_id: UUID) -> Dict:
        """Return a single node by request parameters (placeholder)."""
        return self.service_layer_rpc_client.get_node(node_id)

    def register_node(self, request: NodeRegisterRequest) -> Dict:
        """Register a node using the incoming request payload."""
        return self.service_layer_rpc_client.register_node(
            RegisterNodeServiceCommand.model_validate(request)
        )

    def heartbeat(self, request: HeartbeatRequest) -> Dict:
        """Send a heartbeat payload."""
        return self.service_layer_rpc_client.heartbeat(
            HeartbeatServiceCommand.model_validate(request)
        )

    def choose_node(self, request: VmPlacementRequest) -> Dict:
        """Select a node for VM placement based on request parameters."""
        return self.service_layer_rpc_client.choose_node(
            PlacementRequestServiceCommand.model_validate(request)
        )

    def get_cluster_events(self, filters: Dict) -> List[Dict]:
        """Return cluster events filtered by given criteria."""
        return self.service_layer_rpc_client.get_cluster_events(filters)
