"""Some description"""
from typing import Dict, List

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.event_store import (
    EventstoreServiceLayerProtocolInterface,
)


class EventstoreServiceLayerRPCClient(EventstoreServiceLayerProtocolInterface):
    """Some description"""
    def __init__(self, module_name: str) -> None:
        """Some description"""
        self.module_name = module_name
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.Eventstore.SERVICE_LAYER
        )

    def get_all_events(self) -> List:
        """Some description"""
        events: List = self.service_rpc_client.call(
            EventstoreServiceLayerProtocolInterface.get_all_events.__name__,
            data_for_method={},
        )
        return events

    def add_event(self, data: Dict) -> None:
        """Some description"""
        data.update({'module': self.module_name})
        self.service_rpc_client.call(
            EventstoreServiceLayerProtocolInterface.add_event.__name__,
            data_for_method=data,
        )
