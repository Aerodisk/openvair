"""Module for managing event-related operations in the service layer.

This module provides functionality for handling event operations such as
adding and getting event data.

The module includes an interface definition for the eventstore service layer
manager which outlines the methods that should be implemented by any class
responsible for handling event operations.

Classes:
    EventstoreServiceLayerProtocolInterface: Interface for handling eventstore
        service layer operations.
"""

from uuid import UUID
from typing import List, Union, Protocol


class EventstoreServiceLayerProtocolInterface(Protocol):
    """Interface for the EventstoreServiceLayerManager."""

    def get_all_events(self) -> List:
        """Retrieve all events from the database.

        Returns:
            List: List of serialized event data.
        """
        ...

    def get_all_events_by_module(self) -> List:
        """Retrieve all events by module from the database.

        Returns:
            List: List of serialized event data.
        """
        ...

    def get_last_events(self, limit: int) -> List:
        """Retrieve last events from the database.

        Args:
            limit (int): The maximum number of recent events to retrieve.

        Returns:
            List: List of serialized event data.
        """
        ...

    def add_event(
        self,
        object_id: Union[UUID, str],
        user_id: Union[UUID, str],
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
        ...
