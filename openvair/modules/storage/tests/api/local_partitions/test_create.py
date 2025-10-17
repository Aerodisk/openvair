"""Integration tests for local partition creation.

Covers:
- Successful local disk partition creation.
- Validation errors (insufficient_space).
- Logical errors (nonexistent disk).
- Unauthorized access.
"""

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import get_disk_partitions


def test_create_local_partition_success(
    client: TestClient, target_disk_path: str
) -> None:
    """Test successful creation of local disk partition."""
    partition_data = {
        'local_disk_path': target_disk_path,
        'storage_type': 'local_partition',
        'size_value': 10 * 1000 * 1000,  # 10 MB
        'size_unit': 'B',
    }

    response = client.post(
        '/storages/local-disks/create_partition/', json=partition_data
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert 'path' in result
    assert 'size' in result
    assert result['parent'] == target_disk_path
    assert result['size'] > 0
    assert result['path'].startswith(target_disk_path)
    partition_number = result['path'].replace(target_disk_path, '')
    assert partition_number in get_disk_partitions(target_disk_path)


def test_create_local_partition_nonexistent_disk(client: TestClient) -> None:
    """Test partition creation on nonexistent disk."""
    partition_data = {
        'local_disk_path': '/nonexistent/disk',
        'storage_type': 'local_partition',
        'size_value': 10 * 1000 * 1000,  # 10 MB
        'size_unit': 'B',
    }

    response = client.post(
        '/storages/local-disks/create_partition/', json=partition_data
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'does not exist' in response.text.lower()


def test_create_local_partition_insufficient_space(
    client: TestClient, target_disk_path: str
) -> None:
    """Test partition creation with insufficient disk space."""
    partition_data = {
        'local_disk_path': target_disk_path,
        'storage_type': 'local_partition',
        'size_value': 10 * 1000 * 1000 * 1000 * 1000,  # 10 TB
        'size_unit': 'B',
    }

    response = client.post(
        '/storages/local-disks/create_partition/', json=partition_data
    )
    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]


def test_create_local_partition_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized partition creation."""
    partition_data = {
        'local_disk_path': '/some/path',
        'storage_type': 'local_partition',
        'size_value': 10 * 1000 * 1000,  # 10 MB
        'size_unit': 'B',
    }

    response = unauthorized_client.post(
        '/storages/local-disks/create_partition/', json=partition_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
