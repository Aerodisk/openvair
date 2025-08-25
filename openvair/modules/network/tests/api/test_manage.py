"""Integration tests for interface manage (turn on/off).

Covers:
- Successful interface turn on
- Successful interface turn off
- Turn on/off non-existent interface
- Unauthorized access
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import wait_for_field_value

LOG = get_logger(__name__)


def test_turn_on_interface_success(
    client: TestClient, pre_turned_off_interface: Dict
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


def test_turn_off_interface_success(
    client: TestClient, pre_turned_on_interface: Dict
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


def test_turn_on_interface_twice(
    client: TestClient, pre_turned_on_interface: Dict
) -> None:
    """Test turning on already on interface.

    Asserts:
    - Response is 200 OK both times
    - Interface remains 'UP'
    """
    interface_name = pre_turned_on_interface['name']

    response = client.request('PUT', f'/interfaces/{interface_name}/turn_on')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/interfaces/{pre_turned_on_interface["id"]}/')
    assert response.json()['power_state'] == 'UP'


def test_turn_off_interface_twice(
    client: TestClient, pre_turned_off_interface: Dict
) -> None:
    """Test turning off already off interface.

    Asserts:
    - Response is 200 OK both times
    - Interface remains 'DOWN'
    """
    interface_name = pre_turned_off_interface['name']

    response = client.request('PUT', f'/interfaces/{interface_name}/turn_off')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/interfaces/{pre_turned_off_interface["id"]}/')
    assert response.json()['power_state'] == 'DOWN'


def test_turn_on_interface_unauthorized(
    pre_turned_off_interface: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized interface turn on.

    Asserts:
    - Response is 401 UNAUTHORIZED
    """
    interface_name = pre_turned_off_interface['name']

    response = unauthorized_client.request(
        'PUT', f'/interfaces/{interface_name}/turn_on'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_turn_off_interface_unauthorized(
    pre_turned_on_interface: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized interface turn off.

    Asserts:
    - Response is 401 UNAUTHORIZED
    """
    interface_name = pre_turned_on_interface['name']

    response = unauthorized_client.request(
        'PUT', f'/interfaces/{interface_name}/turn_off'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
