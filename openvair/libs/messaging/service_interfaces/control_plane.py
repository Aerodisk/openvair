from abc import ABC, abstractmethod  # noqa: D100
from typing import Dict, List, Generic, Mapping, TypeVar

from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)

TNode_co = TypeVar('TNode_co', covariant=True)  # тип узла (DTO/TypedDict/dict)
TEvent_co = TypeVar('TEvent_co', covariant=True)  # тип события кластера
TMap = Mapping[str, object]  # базовый маппинг для фильтров/словарей


class ControlPlaneServiceABC(Generic[TNode_co, TEvent_co], ABC):
    """Generic control-plane service interface."""

    @abstractmethod
    def get_nodes(self) -> List[TNode_co]: ...  # noqa: D102
    @abstractmethod
    def get_node(self, node_id: str) -> TNode_co: ...  # noqa: D102
    @abstractmethod
    def register_node(  # noqa: D102
        self, payload: RegisterNodeServiceCommand
    ) -> TNode_co: ...
    @abstractmethod
    def heartbeat(  # noqa: D102
        self, payload: HeartbeatServiceCommand
    ) -> Dict[str, object]: ...
    @abstractmethod
    def choose_node(  # noqa: D102
        self, payload: PlacementRequestServiceCommand
    ) -> Dict[str, object]: ...
    @abstractmethod
    def get_cluster_events(self, filters: TMap) -> List[TEvent_co]: ...  # noqa: D102
