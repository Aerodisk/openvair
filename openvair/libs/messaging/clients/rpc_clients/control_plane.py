from typing import Dict, List  # noqa: D100

from openvair.libs.messaging.service_interfaces.control_plane import (
    ControlPlaneServiceABC,
)


class ControlPlaneServiceLayerRPCClient(ControlPlaneServiceABC):  # noqa: D101
    def get_nodes(self) -> List[Dict]:  # noqa: D102
        return []

    def register_node(self, data: Dict) -> Dict:  # noqa: D102, ARG002
        return {}

    def heartbeat(self, data: Dict) -> Dict:  # noqa: D102, ARG002
        return {}

    def choose_node(self, data: Dict) -> Dict:  # noqa: D102, ARG002
        return {}

    def get_cluster_events(self, filters: Dict) -> List[Dict]:  # noqa: D102, ARG002
        return []
