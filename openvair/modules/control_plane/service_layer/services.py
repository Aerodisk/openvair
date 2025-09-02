from typing import Dict  # noqa: D100

from openvair.libs.messaging.messaging_agents import MessagingClient


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


class ControlPlaneServiceLayerManager:  # noqa: D101
    @staticmethod
    def call_vm_on_node(  # noqa: D102
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
            timeout=timeout,
        )
        return resp
