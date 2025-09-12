"""Generic control-plane service interface.

This module defines a generic, transport-agnostic ABC for the control-plane
service. Implementations may return DTOs, TypedDicts, or plain dicts,
depending on the layer (domain vs. RPC client). The interface is generic
and covariant in output types to support domain DTOs and transport shapes
without coupling modules via imports.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict, List, Generic, Mapping, TypeVar

from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)

TNode_co = TypeVar(
    'TNode_co', covariant=True
)  # node representation (DTO/TypedDict/dict)
TEvent_co = TypeVar('TEvent_co', covariant=True)  # cluster event representation
TMap = Mapping[str, object]  # base mapping for filters/payloads


class ControlPlaneServiceABC(Generic[TNode_co, TEvent_co], ABC):
    """Generic control-plane service interface.

    Type parameters:
        TNode_co: Covariant node representation (DTO/TypedDict/dict).
        TEvent_co: Covariant event representation.
    """

    @abstractmethod
    def get_nodes(self) -> List[TNode_co]:
        """Return a collection of nodes."""

    @abstractmethod
    def get_node(self, node_id: UUID) -> TNode_co:
        """Return node details by identifier."""

    @abstractmethod
    def register_node(
        self,
        payload: RegisterNodeServiceCommand,
    ) -> TNode_co:
        """Register a node and return its representation."""

    @abstractmethod
    def heartbeat(
        self,
        payload: HeartbeatServiceCommand,
    ) -> Dict[str, object]:
        """Process a heartbeat message and return a transport payload."""

    @abstractmethod
    def choose_node(
        self,
        payload: PlacementRequestServiceCommand,
    ) -> Dict[str, object]:
        """Select a node for VM placement and return a transport payload."""

    @abstractmethod
    def get_cluster_events(self, filters: TMap) -> List[TEvent_co]:
        """Return cluster events matching provided filters."""
