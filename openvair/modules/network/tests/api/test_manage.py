# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for interface manage (turn on/off).

Covers:
- Successful interface turn on
- Successful interface turn off
- Turn on/off non-existent interface
- Unauthorized access
"""

import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import wait_for_field_value

LOG = get_logger(__name__)


def test_turn_on_interface_success(
    client: TestClient, pre_turned_off_interface: dict
) -> None:
    """Test successful interface turn on.

    Asserts:
    - Response is 200 OK with success message
    - Interface power_state becomes 'UP'
    """
    interface_name = pre_turned_off_interface['name']

    response = client.request('PUT', f'/interfaces/{interface_name}/turn_on')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn on command was sent' in response.text.lower()

    wait_for_field_value(
        client,
        f'/interfaces/{pre_turned_off_interface["id"]}/',
        'power_state',
        'UP',
    )


# TODO: Test OVS only when fixed https://github.com/Aerodisk/openvair/issues/117
#       (or other tests will fail due to network error when using OVS)
@pytest.mark.manager('netplan')
def test_turn_on_bridge_success(
    check_manager: None, client: TestClient, bridge: dict
) -> None:
    """Test successful bridge interface turn on.

    Asserts:
    - Response is 200 OK with success message
    - Bridge interface power_state becomes 'UNKNOWN' (because it's a bridge)
    """
    bridge_name = bridge['name']
    client.request('PUT', f'/interfaces/{bridge_name}/turn_off')
    wait_for_field_value(
        client, f'/interfaces/{bridge["id"]}/', 'power_state', 'DOWN'
    )

    response = client.request('PUT', f'/interfaces/{bridge_name}/turn_on')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn on command was sent' in response.text.lower()

    wait_for_field_value(
        client, f'/interfaces/{bridge["id"]}/', 'power_state', 'UNKNOWN'
    )


def test_turn_on_nonexistent_interface(client: TestClient) -> None:
    """Test turning on non-existent interface.

    Asserts:
    - Response is 500 INTERNAL SERVER ERROR
    - Error message indicates interface not found
    """
    nonexistent_name = f'nonexistent-{uuid.uuid4().hex[:8]}'

    response = client.request('PUT', f'/interfaces/{nonexistent_name}/turn_on')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_turn_on_interface_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized interface turn on.

    Asserts:
    - Response is 401 UNAUTHORIZED
    """
    response = unauthorized_client.request(
        'PUT', f'/interfaces/{"some_interface"}/turn_on'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_turn_off_interface_success(
    client: TestClient, pre_turned_on_interface: dict
) -> None:
    """Test successful interface turn off.

    Asserts:
    - Response is 200 OK with success message
    - Interface power_state becomes 'DOWN'
    """
    interface_name = pre_turned_on_interface['name']

    response = client.request('PUT', f'/interfaces/{interface_name}/turn_off')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn off command was sent' in response.text.lower()

    wait_for_field_value(
        client,
        f'/interfaces/{pre_turned_on_interface["id"]}/',
        'power_state',
        'DOWN',
    )


# TODO: Test OVS only when fixed https://github.com/Aerodisk/openvair/issues/117
#       (or other tests will fail due to network error when using OVS)
@pytest.mark.manager('netplan')
def test_turn_off_bridge_success(
    check_manager: None, client: TestClient, bridge: dict
) -> None:
    """Test successful bridge interface turn off.

    Asserts:
    - Response is 200 OK with success message
    - Bridge interface power_state becomes 'DOWN'
    """
    bridge_name = bridge['name']
    client.request('PUT', f'/interfaces/{bridge_name}/turn_on')
    wait_for_field_value(
        client, f'/interfaces/{bridge["id"]}/', 'power_state', 'UNKNOWN'
    )

    response = client.request('PUT', f'/interfaces/{bridge_name}/turn_off')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn off command was sent' in response.text.lower()

    wait_for_field_value(
        client, f'/interfaces/{bridge["id"]}/', 'power_state', 'DOWN'
    )


def test_turn_off_nonexistent_interface(client: TestClient) -> None:
    """Test turning off non-existent interface.

    Asserts:
    - Response is 500 INTERNAL SERVER ERROR
    - Error message indicates interface not found
    """
    nonexistent_name = f'nonexistent-{uuid.uuid4().hex[:8]}'

    response = client.request('PUT', f'/interfaces/{nonexistent_name}/turn_off')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_turn_off_interface_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized interface turn off.

    Asserts:
    - Response is 401 UNAUTHORIZED
    """
    response = unauthorized_client.request(
        'PUT', f'/interfaces/{"some_interface"}/turn_off'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
