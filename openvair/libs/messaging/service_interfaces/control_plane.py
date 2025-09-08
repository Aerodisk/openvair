from abc import ABC, abstractmethod  # noqa: D100
from typing import Dict, List

from openvair.libs.contracts.control_plane_service import (
    HeartbeatServiceCommand,
    RegisterNodeServiceCommand,
    PlacementRequestServiceCommand,
)


class ControlPlaneServiceABC(ABC):  # noqa: D101
    @abstractmethod
    def get_nodes(self) -> List[Dict]: ...  # noqa: D102
    @abstractmethod
    def register_node(self, payload: RegisterNodeServiceCommand) -> Dict: ...  # noqa: D102
    @abstractmethod
    def heartbeat(self, payload: HeartbeatServiceCommand) -> Dict: ...  # noqa: D102
    @abstractmethod
    def choose_node(self, payload: PlacementRequestServiceCommand) -> Dict: ...  # noqa: D102
    @abstractmethod
    def get_cluster_events(self, filters: Dict) -> List[Dict]: ...  # noqa: D102
