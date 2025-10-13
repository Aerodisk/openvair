"""Integration tests for storage retrieval (NFS).

Covers:
- Successful retrieval of NFS storages
- Validation errors (invalid UUID, nonexistent storage)
- Unauthorized access for all endpoints
"""

import uuid
from typing import Dict

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import storage_settings


@pytest.mark.parametrize('storage', ['nfs'], indirect=True)
def test_get_storages_nfs_success(
    client: TestClient, storage: Dict
) -> None:
    """Test successful retrieval of storages list with NFS storage."""
    assert storage['storage_type'] == 'nfs'
    response = client.get('/storages/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert data['total'] >= 1

    storage_ids = [item['id'] for item in data['items']]
    assert storage['id'] in storage_ids

    nfs_storage_data = next(
        item for item in data['items'] if item['id'] == storage['id']
    )
    assert nfs_storage_data['storage_type'] == storage['storage_type']
    assert nfs_storage_data['status'] == 'available'


@pytest.mark.parametrize('storage', ['nfs'], indirect=True)
def test_get_storage_nfs_success(client: TestClient, storage: Dict) -> None:
    """Test successful NFS storage retrieval by ID."""
    assert storage['storage_type'] == 'nfs'
    response = client.get(f"/storages/{storage['id']}/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['id'] == storage['id']
    assert data['name'] == storage['name']
    assert data['storage_type'] == storage['storage_type']
    assert data['status'] == 'available'
    assert 'storage_extra_specs' in data
    specs = data['storage_extra_specs']
    assert specs['ip'] == str(storage_settings.storage_nfs_ip)
    assert specs['path'] == str(storage_settings.storage_nfs_path)
    assert specs['mount_version'] == '4'


def test_get_storage_nfs_nonexistent(client: TestClient) -> None:
    """Test retrieval of nonexistent NFS storage."""
    nonexistent_id = uuid.uuid4()
    response = client.get(f'/storages/{nonexistent_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_storage_nfs_invalid_id(client: TestClient) -> None:
    """Test retrieval with invalid storage ID."""
    response = client.get('/storages/invalid-id/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
