"""Integration tests for retrieving virtual networks via API.

Covers:
- List retrieval when data exists
- Retrieving single virtual network by ID
- Handling invalid UUID on GET by ID
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def test_get_virtual_networks_success(
    client: TestClient, virtual_network: Dict
) -> None:
    """List endpoint returns created network in results."""
    response = client.get('/virtual_networks/')
    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()
    assert 'virtual_networks' in data
    assert any(v['id'] == virtual_network['id'] for v in data['virtual_networks'])


def test_get_virtual_network_by_id_success(
    client: TestClient, virtual_network: Dict
) -> None:
    """GET by ID returns the expected object."""
    vnet_id = virtual_network['id']
    response = client.get(f'/virtual_networks/{vnet_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == vnet_id
    assert data['network_name'] == virtual_network['network_name']


def test_get_virtual_network_by_id_invalid_uuid(client: TestClient) -> None:
    """Invalid UUID should yield 400/422 depending on validation chain."""
    response = client.get('/virtual_networks/not-a-uuid/')
    assert response.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY}  # noqa: E501 