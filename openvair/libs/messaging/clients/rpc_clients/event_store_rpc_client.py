"""Proxy implementation for the Eventstore Service Layer.

This module defines the `EventstoreServiceLayerRPCClient` class, which serves as
a proxy for interacting with the Eventstore Service Layer. The proxy class
encapsulates the details of the RPC communication with the service layer,
providing a consistent and easy-to-use interface for external code.

The `EventstoreServiceLayerRPCClient` class implements the
`EventstoreServiceLayerProtocolInterface`, which defines the contract for
interacting with the Eventstore service layer. This allows the external code
to work with the proxy class without needing to know the underlying
implementation details.

Classes:
    EventstoreServiceLayerRPCClient: Proxy implementation for the Eventstore
        Service Layer, providing a consistent interface for interacting with the
        Eventstore service.
"""

from typing import Dict, List

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.event_store import (
    EventstoreServiceLayerProtocolInterface,
)


class EventstoreServiceLayerRPCClient(EventstoreServiceLayerProtocolInterface):
    """Proxy implementation for EventstoreServiceLayerProtocolInterface

    This class provides methods to interact with the Eventstore Service Layer
    through RPC calls.

    Attributes:
        service_rpc_client (RabbitRPCClient): RPC client for communicating with
            the Eventstore Service Layer.
        module_name: the name of the module for events
    """

    def __init__(self, module_name: str) -> None:
        """Initialize the EventstoreServiceLayerRPCClient.

        This method sets up the necessary components for the
        EventstoreServiceLayerRPCClient.
        """
        self.module_name = module_name
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.Eventstore.SERVICE_LAYER
        )

    def get_all_events(self) -> List:
        """Retrieve all events from the database.

        Returns:
            List: List of serialized event data.
        """
        events: List = self.service_rpc_client.call(
            EventstoreServiceLayerProtocolInterface.get_all_events.__name__,
            data_for_method={},
        )
        return events

    def add_event(self, data: Dict) -> None:
        """Add a new event to the db.

        Args:
            data (Dict): Information about the event.

        Returns:
            None.
        """
        data.update({'module': self.module_name})
        self.service_rpc_client.call(
            EventstoreServiceLayerProtocolInterface.add_event.__name__,
            data_for_method=data,
        )
