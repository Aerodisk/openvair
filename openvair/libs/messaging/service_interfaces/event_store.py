"""Some description"""

from typing import List, Protocol


class EventstoreServiceLayerProtocolInterface(Protocol):
    """Interface for the EventstoreServiceLayerManager."""

    def get_all_events(self) -> List:
        """Some description"""
        ...
