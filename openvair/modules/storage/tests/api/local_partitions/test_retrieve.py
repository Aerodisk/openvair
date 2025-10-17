"""Integration tests for local partitions (disks) retrieval.

Covers:
- Successful retrieval (local disks, partitions).
- Validation errors (missing param).
- Logical errors (invalid disk).
- Unauthorized access.
"""

from typing import Dict, List

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import storage_settings


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
