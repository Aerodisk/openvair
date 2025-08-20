# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for backup creation via API.

Covers:
- Successful backup creation
- Creation backup without repository
- Unauthorized access
"""

from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.backup.config import RESTIC_PASSWORD
from openvair.modules.backup.adapters.restic.restic import ResticAdapter


def test_create_backup_success(
    client: TestClient,
    backup_repository: Path,
) -> None:
    """Test successful backup creation flow.

    Asserts:
    - API returns 200 on backup creation
    - Response contains valid snapshot metadata
    - Snapshot appears in backups list
    """
    response = client.post('/backup/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'success'
    backup_data = data['data']
    assert isinstance(backup_data['snapshot_id'], str)
    assert isinstance(backup_data['total_files_processed'], int)
    assert isinstance(backup_data['files_new'], int)
    assert isinstance(backup_data['files_changed'], int)
    assert isinstance(backup_data['files_unmodified'], int)
    assert isinstance(backup_data['data_added_packed'], int)
    assert data['error'] is None

    list_response = client.get('/backup/')
    assert list_response.status_code == status.HTTP_200_OK
    snapshots = list_response.json()['data']
    assert any(s['id'] == backup_data['snapshot_id'] for s in snapshots)

    restic_adapter = ResticAdapter(backup_repository, RESTIC_PASSWORD)
    restic_snapshots = restic_adapter.snapshots()
    assert len(restic_snapshots) == 1
    assert backup_data['snapshot_id'] == restic_snapshots[0]['id']


def test_create_backup_without_repository(
    client: TestClient,
    clean_backup_repository: Path,
) -> None:
    """Test backup creation without initialized repository.

    Asserts:
    - Returns 500 Internal Server Error
    - Error message indicates missing repository
    """
    response = client.post('/backup/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'repository does not exist' in response.json()['message'].lower()


def test_create_backup_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized backup creation.

    Asserts:
    - Returns 401 Unauthorized
    """
    response = unauthorized_client.post('/backup/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
