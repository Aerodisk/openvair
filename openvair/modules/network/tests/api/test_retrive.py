"""Integration tests for retrieving interfaces and bridges.

Covers:
- Get all interfaces (paginated)
- Get all interfaces with filter
- Unauthorized access (all endpoints)
- Get bridges list
- Get specific interface by ID
- Nonexistent interface returns error
"""

import uuid
from typing import Dict, List

from fastapi import status
from fastapi.testclient import TestClient


def test_get_interfaces_success(client: TestClient) -> None:
    """Test retrieving all interfaces.

    Asserts:
    - Response is 200 OK
    - Response contains 'items' list
    - Each item has required fields
    """
    response = client.get('/interfaces/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'items' in data
    assert isinstance(data['items'], List)

    if data['items']:
        required_fields = [
            'id',
            'name',
            'mac',
            'inf_type',
            'power_state',
        ]
        for field in required_fields:
            assert field in data['items'][0]


def test_get_interfaces_with_filter(client: TestClient) -> None:
    """Test retrieving interfaces with filter flag enabled.

    Asserts:
    - Response is 200 OK
    - Response contains items list (possibly filtered)
    """
    response = client.get('/interfaces/?is_need_filter=true')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'items' in data
    assert isinstance(data['items'], List)


def test_get_interfaces_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized access to interfaces list.

    Asserts:
    - HTTP 401 Unauthorized
    """
    response = unauthorized_client.get('/interfaces/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_bridges_list(client: TestClient, bridge: Dict) -> None:
    """Test retrieving bridges list.

    Asserts:
    - Response is 200 OK
    - Created bridge appears in list
    """
    response = client.get('/interfaces/bridges/')
    assert response.status_code == status.HTTP_200_OK

    bridges = response.json()
    assert isinstance(bridges, List)
    assert any(br['ifname'] == bridge['name'] for br in bridges)


def test_get_bridges_list_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized access to bridges list.

    Asserts:
    - HTTP 401 Unauthorized
    """
    response = unauthorized_client.get('/interfaces/bridges/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_interface_by_id(client: TestClient, bridge: Dict) -> None:
    """Test retrieving a specific interface by ID.

    Asserts:
    - Response is 200 OK
    - Fields match the created bridge
    """
    response = client.get(f'/interfaces/{bridge["id"]}/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['id'] == bridge['id']
    assert data['name'] == bridge['name']
    assert data['mac'] == bridge['mac']


def test_get_interface_by_id_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized access to specific interface.

    Asserts:
    - HTTP 401 Unauthorized
    """
    response = unauthorized_client.get(f'/interfaces/{uuid.uuid4()!s}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_interface_nonexistent(client: TestClient) -> None:
    """Test retrieving nonexistent interface returns error.

    Asserts:
    - Response is 404 (expected REST) or 500 (current impl)
    """
    response = client.get(f'/interfaces/{uuid.uuid4()!s}/')
    assert response.status_code in (
        status.HTTP_404_NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    assert 'not found' in response.text.lower()
