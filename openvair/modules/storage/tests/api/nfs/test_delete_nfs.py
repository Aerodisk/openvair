"""Integration tests for NFS storage deletion (NFS).

Covers:
- Successful NFS storage deletion.
- Validation errors (invalid UUID).
- Logical errors:
    - Nonexistent storage
    - Storage with attached volumes/templates
- Unauthorized access.
"""

from uuid import uuid4
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import cleanup_all_volumes
from openvair.modules.storage.service_layer.services import StorageStatus


def test_delete_storage_nfs_success(
    client: TestClient,
    nfs_storage: Dict,
) -> None:
    """Test successful NFS storage deletion using fixture."""
    storage_id = nfs_storage['id']
    delete_response = client.delete(f'/storages/{storage_id}/delete')
    assert delete_response.status_code == status.HTTP_202_ACCEPTED
    data = delete_response.json()
    assert data['id'] == storage_id
    assert data['status'] == StorageStatus.deleting.name


def test_delete_storage_nfs_invalid_uuid(client: TestClient) -> None:
    """Test deletion with invalid UUID format."""
    response = client.delete('/storages/invalid-uuid/delete')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'uuid' in response.text.lower()


def test_delete_storage_nfs_not_found(client: TestClient) -> None:
    """Test deletion of nonexistent NFS storage."""
    non_existent_id = str(uuid4())
    response = client.delete(f'/storages/{non_existent_id}/delete')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_delete_storage_nfs_with_attached_volume(
    client: TestClient,
    nfs_volume: Dict,
) -> None:
    """Test deletion failure when NFS storage has attached volume."""
    storage_id = nfs_volume['storage_id']
    response = client.delete(f'/storages/{storage_id}/delete')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    response_text = response.text.lower()
    assert 'storagehasobjects' in response_text
    assert 'has volumes' in response.text.lower()


def test_delete_storage_nfs_with_attached_template(
    client: TestClient, nfs_template: Dict, nfs_storage: Dict
) -> None:
    """Test deletion failure when NFS storage has attached template."""
    storage_id = nfs_storage['id']
    cleanup_all_volumes()
    template_response = client.get(f'/templates/{nfs_template["id"]}/')
    assert template_response.status_code == status.HTTP_200_OK
    template_data = template_response.json()['data']
    assert template_data['storage_id'] == storage_id

    response = client.delete(f'/storages/{storage_id}/delete')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    response_text = response.text.lower()
    assert 'storagehasobjects' in response_text
    assert 'has templates' in response.text.lower()


def test_delete_storage_nfs_unauthorized(
    nfs_storage: Dict,
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized NFS storage deletion."""
    storage_id = nfs_storage['id']
    response = unauthorized_client.delete(f'/storages/{storage_id}/delete')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
