"""Fixtures for network integration tests.

Provides:
- `cleanup_bridges`: Deletes all test bridges before and after test.
"""

from typing import Any, cast
from collections.abc import Generator

import pytest
from pytest import Config
from _pytest.fixtures import FixtureRequest
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    cleanup_test_bridges,
    wait_for_field_value,
)
from openvair.libs.testing.config import network_settings
from openvair.modules.network.config import NETWORK_CONFIG_MANAGER

LOG = get_logger(__name__)


def pytest_configure(config: Config) -> None:
    """Register custom manager markers for pytest."""
    config.addinivalue_line('markers', 'ovs: test for OVS manager only')
    config.addinivalue_line('markers', 'netplan: test for Netplan manager only')


@pytest.fixture
def check_manager(request: FixtureRequest) -> None:
    """Skip test if manager doesn't match marker."""
    marker = request.node.get_closest_marker('manager')
    if marker:
        required_manager = marker.args[0]
        if required_manager != NETWORK_CONFIG_MANAGER:
            message = (
                f'Test currently requires {required_manager}, '
                f'actual manager: {NETWORK_CONFIG_MANAGER}'
            )
            pytest.skip(message)


@pytest.fixture
def cleanup_bridges() -> Generator[None, Any, None]:
    """Delete all test bridges before and after test."""
    cleanup_test_bridges()
    yield
    cleanup_test_bridges()


@pytest.fixture
def interface_without_ip(client: TestClient) -> dict | None:
    """Get an interface without IP."""
    response = client.get('/interfaces/')
    interfaces_data = response.json()
    interfaces = interfaces_data.get('items', [])

    for interface in interfaces:
        if (
            interface['name'] != network_settings.network_interface
            and not interface['ip']
            and interface['inf_type'] == 'physical'
        ):
            return cast('dict', interface)
    pytest.skip()
    return None


@pytest.fixture
def pre_turned_off_interface(
    client: TestClient, physical_interface: dict
) -> Generator[dict, None, None]:
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
    client: TestClient, physical_interface: dict
) -> Generator[dict, None, None]:
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
