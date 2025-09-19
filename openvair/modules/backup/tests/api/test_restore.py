# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for restoring backups via API.

Covers:
- Successful restore from latest snapshot
- Successful restore from specific snapshot ID
- Handling of nonexistent snapshot
- Unauthorized access protection
- Empty repository case
- Response structure validation
"""

import uuid
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient


def test_restore_backup_latest_snapshot_success(
    client: TestClient, backup_snapshot: dict
) -> None:
    """Test successful restore of the latest snapshot.

    Asserts:
    - 200 OK status code
    - Correct response structure
    - Success status
    - Empty error field
    - Expected fields in restore data
    - Valid data types
    """
    response = client.post('/backup/restore')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'success'
    assert data['error'] is None

    restore_data = data['data']
    assert isinstance(restore_data, dict)

    expected_fields = {
        'total_files',
        'files_restored',
        'files_skipped',
        'total_bytes',
        'bytes_restored',
        'bytes_skipped',
    }
    assert set(restore_data.keys()) == expected_fields

    assert isinstance(restore_data['total_files'], int)
    assert isinstance(restore_data['files_restored'], int)
    assert isinstance(restore_data['files_skipped'], int)


def test_restore_backup_specific_snapshot_success(
    client: TestClient, backup_snapshot: dict
) -> None:
    """Test restore from specific snapshot ID.

    Asserts:
    - 200 OK status code
    - Correct response structure
    - Success status
    - Empty error field
    - Expected fields in restore data
    - Valid data types
    """
    snapshot_id = backup_snapshot['snapshot_id']
    response = client.post(f'/backup/restore?snapshot_id={snapshot_id}')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'success'
    assert data['error'] is None

    restore_data = data['data']
    assert isinstance(restore_data, dict)

    expected_fields = {
        'total_files',
        'files_restored',
        'files_skipped',
        'total_bytes',
        'bytes_restored',
        'bytes_skipped',
    }
    assert set(restore_data.keys()) == expected_fields

    assert isinstance(restore_data['total_files'], int)
    assert isinstance(restore_data['files_restored'], int)
    assert isinstance(restore_data['files_skipped'], int)


def test_restore_backup_nonexistent_snapshot(
    client: TestClient, backup_repository: Path
) -> None:
    """Test handling of invalid snapshot ID.

    Asserts:
    - HTTP 500
    - Error message
    """
    non_existent_id = str(uuid.uuid4())
    response = client.post(f'/backup/restore?snapshot_id={non_existent_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    data = response.json()
    assert len(data['error']) > 0
    assert len(data['message']) > 0
    assert 'failed to find snapshot' in data['message'].lower()


def test_restore_backup_no_init_repository(
    client: TestClient, clean_backup_repository: Path
) -> None:
    """Test restore attempt from non-initialized repository.

    Asserts:
    - HTTP 500
    - Appropriate error message
    """
    response = client.post('/backup/restore')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    data = response.json()
    assert len(data['error']) > 0
    assert len(data['message']) > 0
    assert 'repository does not exist' in data['message'].lower()


def test_restore_backup_unauthorized(unauthorized_client: TestClient) -> None:
    """Test authentication requirements.

    Asserts:
    - 401 Unauthorized status
    """
    response = unauthorized_client.post('/backup/restore')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
