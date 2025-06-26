"""Some description"""

from typing import Dict, List, Protocol


class EventstoreServiceLayerProtocolInterface(Protocol):
    """Interface for the EventstoreServiceLayerManager."""

    def get_all_events(self) -> List:
        """Some description"""
        ...

    def add_event(self, data: Dict) -> None:
        """Some description"""
        ...
