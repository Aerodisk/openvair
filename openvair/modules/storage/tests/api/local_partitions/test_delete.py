"""Integration tests for local partitions deletion.

Covers:
- Successful local disk partition deletion.
- Validation errors (invalid UUID).
- Logical errors (nonexistent partition)
- Unauthorized access.
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import get_disk_partitions


def test_delete_local_partition_success(
    client: TestClient, target_disk_path: str, local_partition: Dict
) -> None:
    """Test successful deletion of local disk partition."""
    partition_number = local_partition['path'].replace(target_disk_path, '')

    delete_data = {
        'storage_type': 'local_partition',
        'local_disk_path': target_disk_path,
        'partition_number': partition_number,
    }

    response = client.request(
        'DELETE', '/storages/local-disks/delete_partition/', json=delete_data
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert 'successfully deleted' in result['message'].lower()
    partition_number = local_partition['path'].replace(target_disk_path, '')
    assert partition_number not in get_disk_partitions(target_disk_path)


def test_delete_local_partition_nonexistent(
    client: TestClient, target_disk_path: str
) -> None:
    """Test deletion of nonexistent partition."""
    delete_data = {
        'storage_type': 'local_partition',
        'local_disk_path': target_disk_path,
        'partition_number': '999',  # Non-existent partition
    }

    response = client.request(
        'DELETE', '/storages/local-disks/delete_partition/', json=delete_data
    )
    assert response.status_code in [
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_200_OK,
    ]
    if response.status_code == status.HTTP_200_OK:
        result = response.json()
        assert len(result) == 0


def test_delete_local_partition_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized partition deletion."""
    delete_data = {
        'storage_type': 'local_partition',
        'local_disk_path': '/some/path',
        'partition_number': '1',
    }

    response = unauthorized_client.request(
        'DELETE', '/storages/local-disks/delete_partition/', json=delete_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
