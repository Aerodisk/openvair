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

from typing import Dict, List, Protocol


class EventstoreServiceLayerProtocolInterface(Protocol):
    """Interface for the EventstoreServiceLayerManager."""

    def get_all_events(self) -> List:
        """Retrieve all events from the database.

        Returns:
            List: List of serialized event data.
        """
        ...

    def get_all_events_by_module(self, data: Dict) -> List:
        """Retrieve all events by module from the database.

        Returns:
            List: List of serialized event data.
        """
        ...

    def get_last_events(self, data: Dict) -> List:
        """Retrieve last events from the database.

        Returns:
            List: List of serialized event data.
        """
        ...

    def add_event(self, data: Dict) -> None:
        """Add a new event to the db.

        Args:
            data (Dict): Information about the event.

        Returns:
            None.
        """
        ...
