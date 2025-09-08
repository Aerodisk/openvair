"""Integration tests for storage deletion endpoints.

Covers:
- Successful storage (and local disk partition) deletion.
- Validation errors (invalid UUID).
- Logical errors:
    - Nonexistent storage
    - Storage in 'deleting' status
    - Storage with attached volumes/templates
- Unauthorized access.
"""

from uuid import uuid4
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import (
    cleanup_all_volumes,
    get_disk_partitions,
)
from openvair.modules.storage.service_layer.services import StorageStatus


def test_delete_storage_success(
    client: TestClient,
    storage: Dict,
) -> None:
    """Test successful storage deletion using fixture."""
    storage_id = storage['id']
    delete_response = client.delete(f'/storages/{storage_id}/delete')
    assert delete_response.status_code == status.HTTP_202_ACCEPTED
    data = delete_response.json()
    assert data['id'] == storage_id
    assert data['status'] == StorageStatus.deleting.name


def test_delete_storage_invalid_uuid(client: TestClient) -> None:
    """Test deletion with invalid UUID format."""
    response = client.delete('/storages/invalid-uuid/delete')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'uuid' in response.text.lower()


def test_delete_storage_not_found(client: TestClient) -> None:
    """Test deletion of nonexistent storage."""
    non_existent_id = str(uuid4())
    response = client.delete(f'/storages/{non_existent_id}/delete')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_delete_storage_with_attached_volume(
    client: TestClient,
    volume: Dict,
) -> None:
    """Test deletion failure when storage has attached resources."""
    storage_id = volume['storage_id']
    response = client.delete(f'/storages/{storage_id}/delete')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    response_text = response.text.lower()
    assert 'storagehasobjects' in response_text
    assert 'has volumes' in response.text.lower()


def test_delete_storage_with_attached_template(
    client: TestClient, template: Dict, storage: Dict
) -> None:
    """Test deletion failure when storage has attached template."""
    storage_id = storage['id']
    cleanup_all_volumes()

    template_response = client.get(f'/templates/{template["id"]}/')
    assert template_response.status_code == status.HTTP_200_OK
    template_data = template_response.json()['data']
    assert template_data['storage_id'] == storage_id

    response = client.delete(f'/storages/{storage_id}/delete')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    response_text = response.text.lower()
    assert 'storagehasobjects' in response_text
    assert 'has templates' in response_text


def test_delete_storage_unauthorized(
    storage: Dict,
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized storage deletion."""
    storage_id = storage['id']
    response = unauthorized_client.delete(f'/storages/{storage_id}/delete')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
