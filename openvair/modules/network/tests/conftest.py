"""Fixtures for network integration tests.

Provides:
- `cleanup_bridges`: Deletes all test bridges before and after test.
"""

from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    cleanup_test_bridges,
    wait_for_field_value,
)

LOG = get_logger(__name__)


@pytest.fixture
def cleanup_bridges() -> Generator[None, Any, None]:
    """Delete all test bridges before and after test."""
    cleanup_test_bridges()
    yield
    cleanup_test_bridges()


@pytest.fixture
def pre_turned_off_interface(
    client: TestClient, physical_interface: Dict
) -> Generator[Dict, None, None]:
    """Turn the interface off before the test."""
    interface_name = physical_interface['name']
    client.request('PUT', f'/interfaces/{interface_name}/turn_off')
    wait_for_field_value(
        client,
        f'/interfaces/{physical_interface["id"]}/',
        'power_state',
        'DOWN',
    )

    yield physical_interface

    client.request('PUT', f'/interfaces/{interface_name}/turn_on')
    wait_for_field_value(
        client, f'/interfaces/{physical_interface["id"]}/', 'power_state', 'UP'
    )


@pytest.fixture
def pre_turned_on_interface(
    client: TestClient, physical_interface: Dict
) -> Generator[Dict, None, None]:
    """Turn the interface on before the test."""
    interface_name = physical_interface['name']
    client.request('PUT', f'/interfaces/{interface_name}/turn_on')
    wait_for_field_value(
        client, f'/interfaces/{physical_interface["id"]}/', 'power_state', 'UP'
    )

    yield physical_interface

    client.request('PUT', f'/interfaces/{interface_name}/turn_on')
    wait_for_field_value(
        client, f'/interfaces/{physical_interface["id"]}/', 'power_state', 'UP'
    )
