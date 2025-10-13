"""Integration tests for virtual network lifecycle operations.

Covers:
- turn_on endpoint returns 200 and message
- turn_off endpoint returns 200 and message
- Unauthorized access
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def test_turn_on_virtual_network(
    client: TestClient,
    virtual_network: Dict
) -> None:
    """Test successful turn on of the virtual network."""
    response = client.put(f'/virtual_networks/{virtual_network["id"]}/turn_on')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn on' in response.text.lower()


def test_turn_off_virtual_network(
    client: TestClient,
    virtual_network: Dict
) -> None:
    """Test successful turn off of the virtual network."""
    response = client.put(f'/virtual_networks/{virtual_network["id"]}/turn_off')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn off' in response.text.lower()


def test_turn_on_virtual_network_unauthorized(
    virtual_network: Dict,
    unauthorized_client: TestClient
) -> None:
    """Test unauthorized client gets 401 error."""
    response = unauthorized_client.put(
        f'/virtual_networks/{virtual_network["id"]}/turn_on'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_turn_off_virtual_network_unauthorized(
    virtual_network: Dict,
    unauthorized_client: TestClient
) -> None:
    """Test unauthorized client gets 401 error."""
    response = unauthorized_client.put(
        f'/virtual_networks/{virtual_network["id"]}/turn_off'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
