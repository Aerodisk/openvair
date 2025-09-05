"""Fixtures for event store integration tests.

Provides:
- `cleanup_events`: Clean up all events before and after each test
- `created_event`: Create a test event via RPC client and return its data
- `multiple_events`: Create multiple test events via RPC client

Includes:
- `cleanup_all_events`: Utility to delete all events from DB.
"""

from uuid import uuid4
from typing import Dict, List, Generator

import pytest

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import cleanup_all_events
from openvair.libs.messaging.clients.rpc_clients.event_store_rpc_client import (
    EventStoreServiceLayerRPCClient,
)

LOG = get_logger(__name__)


@pytest.fixture(scope="function", autouse=True)
def cleanup_events() -> Generator:
    """Clean up all events before and after each test."""
    cleanup_all_events()
    yield
    cleanup_all_events()


@pytest.fixture(scope="function")
def created_event() -> Dict:
    """Create a test event via service layer and return its data."""
    event_data = {
        "module": "test_module",
        "object_id": str(uuid4()),
        "user_id": str(uuid4()),
        "event": "test_event",
        "information": "test_info"
    }
    event_client = EventStoreServiceLayerRPCClient(event_data["module"])
    event_client.add_event(
        object_id=event_data['object_id'],
        user_id=event_data['user_id'],
        event=event_data['event'],
        information=event_data['information']
    )
    return event_data


@pytest.fixture(scope="function")
def multiple_events() -> List[Dict]:
    """Create multiple test events."""
    events_data = [
        {
            "module": "test_module",
            "object_id": str(uuid4()),
            "user_id": str(uuid4()),
            "event": f"test_event_{i}",
            "information": f"test_info_{i}"
        } for i in range(3)
    ]
    for data in events_data:
        event_client = EventStoreServiceLayerRPCClient(data["module"])
        event_client.add_event(
            object_id=data["object_id"],
            user_id=data["user_id"],
            event=data["event"],
            information=data["information"]
        )
    return events_data
