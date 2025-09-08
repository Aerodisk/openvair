from abc import ABC, abstractmethod  # noqa: D100
from typing import Dict, List


class ControlPlaneServiceABC(ABC):  # noqa: D101
    @abstractmethod
    def get_nodes(self) -> List[Dict]: ...  # noqa: D102
    @abstractmethod
    def register_node(self, data: Dict) -> Dict: ...  # noqa: D102
    @abstractmethod
    def heartbeat(self, data: Dict) -> Dict: ...  # noqa: D102
    @abstractmethod
    def choose_node(self, data: Dict) -> Dict: ...  # noqa: D102
    @abstractmethod
    def get_cluster_events(self, filters: Dict) -> List[Dict]: ...  # noqa: D102
