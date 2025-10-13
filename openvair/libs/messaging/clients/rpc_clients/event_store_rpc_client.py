"""Proxy implementation for the event_store service layer.

This module defines the `EventStoreServiceLayerRPCClient` class, which serves as
a proxy for interacting with the event_store service layer. The proxy class
encapsulates the details of the RPC communication with the service layer,
providing a consistent and easy-to-use interface for external code.

The `EventStoreServiceLayerRPCClient` class implements the
`EventStoreServiceLayerProtocolInterface`, which defines the contract for
interacting with the event_store service layer. This allows the external code
to work with the proxy class without needing to know the underlying
implementation details.

Classes:
    EventStoreServiceLayerRPCClient: Proxy implementation for the event_store
        service layer, providing a consistent interface for interacting with
        the event_store service.
"""

from uuid import UUID

from pydantic import ValidationError

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.contracts.event_store_service import (
    CreateEventServiceCommand,
    GetLastEventsServiceCommand,
    GetEventsByModuleServiceCommand,
)
from openvair.libs.messaging.service_interfaces.event_store import (
    EventStoreServiceLayerProtocolInterface,
)


class EventStoreServiceLayerRPCClient(EventStoreServiceLayerProtocolInterface):
    """Proxy implementation for EventStoreServiceLayerProtocolInterface

    This class provides methods to interact with the event_store service layer
    through RPC calls.

    Attributes:
        service_rpc_client (RabbitRPCClient): RPC client for communicating with
            the event_store service layer.
        module_name: the name of the module for events
    """

    def __init__(self, module_name: str) -> None:
        """Initialize the EventStoreServiceLayerRPCClient.

        This method sets up the necessary components for the
        EventStoreServiceLayerRPCClient.
        """
        self.module_name = module_name
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.EventStore.SERVICE_LAYER
        )

    def get_all_events(self) -> list:
        """Retrieve all events from the database.

        Returns:
            List: List of serialized event data.
        """
        events: list = self.service_rpc_client.call(
            EventStoreServiceLayerProtocolInterface.get_all_events.__name__,
            data_for_method={},
        )
        return events

    def get_all_events_by_module(self) -> list:
        """Retrieve all events by module from the database.

        Returns:
            List: List of serialized event data.
        """
        events: list = self.service_rpc_client.call(
            EventStoreServiceLayerProtocolInterface.get_all_events_by_module.__name__,
            data_for_method=GetEventsByModuleServiceCommand(
                module_name=self.module_name
            ).model_dump(mode='json'),
        )
        return events

    def get_last_events(self, limit: int) -> list:
        """Retrieve last events from the database.

        Args:
            limit (int): The maximum number of recent events to retrieve.

        Returns:
            List: List of serialized event data.
        """
        events: list = self.service_rpc_client.call(
            EventStoreServiceLayerProtocolInterface.get_last_events.__name__,
            data_for_method=GetLastEventsServiceCommand(limit=limit).model_dump(
                mode='json'
            ),
        )
        return events

    def add_event(
        self,
        object_id: UUID | str,
        user_id: UUID | str,
        event: str,
        information: str,
    ) -> None:
        """Add a new event to the db.

        Args:
            object_id (Union[UUID, str]): Unique identifier of the affected
                object.
            user_id (Union[UUID, str]): Unique identifier of the user who
                triggered the event.
            event (str): Type or name of the event.
            information (str): Additional details or context about the event.

        Returns:
            None.
        """
        payload = {
            'module': self.module_name,
            'object_id': object_id,
            'user_id': user_id,
            'event': event,
            'information': information,
        }
        try:
            validated = CreateEventServiceCommand.model_validate(payload)
        except ValidationError as e:
            msg = f'Invalid event payload: {e}'
            raise ValueError(msg) from e
        self.service_rpc_client.cast(
            EventStoreServiceLayerProtocolInterface.add_event.__name__,
            data_for_method=validated.model_dump(mode='json'),
        )
