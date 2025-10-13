"""Integration tests for storage retrieval endpoints.

Covers:
- Successful retrieval (all storages, storage by ID)
- Validation errors (invalid UUID, nonexistent storage, etc.)
- Unauthorized access for all endpoints
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def test_get_storages_success(client: TestClient, storage: Dict) -> None:
    """Test successful retrieval of storages list with storage."""
    assert storage['storage_type'] == 'localfs'
    response = client.get('/storages/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert data['total'] >= 1
    storage_data = data['items'][0]
    assert storage_data['id'] == storage['id']
    assert storage_data['name'] == storage['name']
    assert storage_data['storage_type'] == storage['storage_type']
    assert storage_data['status'] == 'available'


def test_get_storages_empty_success(
    client: TestClient
) -> None:
    """Test successful retrieval of empty storages list."""
    response = client.get('/storages/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['total'] == 0
    assert len(data['items']) == 0


def test_get_storages_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized access to storages list."""
    response = unauthorized_client.get('/storages/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_storage_success(client: TestClient, storage: Dict) -> None:
    """Test successful storage retrieval by ID."""
    assert storage['storage_type'] == 'localfs'
    response = client.get(f"/storages/{storage['id']}/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['id'] == storage['id']
    assert data['name'] == storage['name']
    assert data['storage_type'] == storage['storage_type']
    assert data['status'] == 'available'


def test_get_storage_nonexistent(client: TestClient) -> None:
    """Test retrieval of nonexistent storage."""
    nonexistent_id = uuid.uuid4()
    response = client.get(f'/storages/{nonexistent_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_storage_invalid_id(client: TestClient) -> None:
    """Test retrieval with invalid storage ID."""
    response = client.get('/storages/invalid-id/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_storage_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized access to specific storage."""
    response = unauthorized_client.get(f'/storages/{uuid.uuid4()}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
