"""Integration tests for virtual network lifecycle operations.

Covers:
- turn_on endpoint returns 200 and message
- turn_off endpoint returns 200 and message
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def test_turn_on_virtual_network(client: TestClient, virtual_network: Dict) -> None:
    vnet_id = virtual_network['id']
    response = client.put(f'/virtual_networks/{vnet_id}/turn_on')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn on' in response.text.lower()


def test_turn_off_virtual_network(client: TestClient, virtual_network: Dict) -> None:
    vnet_id = virtual_network['id']
    response = client.put(f'/virtual_networks/{vnet_id}/turn_off')
    assert response.status_code == status.HTTP_200_OK
    assert 'turn off' in response.text.lower() 