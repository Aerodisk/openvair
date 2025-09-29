"""Integration tests for storage retrieval endpoints.

Covers:
- Successful retrieval (all storages, storage by ID, local disks, partitions)
- Validation errors (invalid UUID, nonexistent storage, etc.)
- Unauthorized access for all endpoints
"""

import uuid
from typing import Dict, List

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import storage_settings


def test_get_storages_success(client: TestClient, storage: Dict) -> None:
    """Test successful retrieval of storages list with storage."""
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


def test_get_local_disks_success(client: TestClient) -> None:
    """Test successful retrieval of local disks."""
    response = client.get('/storages/local-disks/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'disks' in data
    assert isinstance(data['disks'], List)
    test_disk_path = str(storage_settings.storage_path)
    api_disk_paths = [disk['path'] for disk in data['disks'] if 'path' in disk]
    assert test_disk_path in api_disk_paths
    for disk in data['disks']:
        assert 'path' in disk
        assert 'size' in disk
        assert isinstance(disk['path'], str)
        assert isinstance(disk['size'], int)
        if disk['path'] == test_disk_path:
            assert disk['size'] > 0
            assert disk['fstype'] == storage_settings.storage_fs_type


def test_get_local_disks_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized access to local disks."""
    response = unauthorized_client.get('/storages/local-disks/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_local_disk_partitions_success(client: TestClient) -> None:
    """Test successful retrieval of disk partition info."""
    disks_response = client.get('/storages/local-disks/')
    disks_data = disks_response.json()

    for disk in disks_data['disks']:
        if disk['parent'] is None:
            disk_path = disk['path']
            response = client.get(
                f'/storages/local-disks/partition_info/?disk_path={disk_path}'
            )
            assert response.status_code == status.HTTP_200_OK
            partition_info = response.json()
            assert isinstance(partition_info, Dict)
            for _, partition in partition_info.items():
                required_fields = [
                    'Number',
                    'Size',
                    'Start',
                    'End',
                    'File system',
                    'Flags',
                ]
                for field in required_fields:
                    assert field in partition


def test_get_local_disk_partitions_invalid_disk(client: TestClient) -> None:
    """Test partition info retrieval with invalid disk path."""
    response = client.get(
        '/storages/local-disks/partition_info/?disk_path=/invalid/path'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_local_disk_partitions_missing_param(client: TestClient) -> None:
    """Test partition info retrieval without required parameter."""
    response = client.get('/storages/local-disks/partition_info/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_local_disk_partitions_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized access to partition info."""
    response = unauthorized_client.get(
        '/storages/local-disks/partition_info/?disk_path=/some/path'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
