# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for deleting backups via API.

Covers:
- Successful deletion of existing snapshot
- Handling of nonexistent snapshot ID
- Unauthorized access protection
- Response structure validation
"""

import uuid
from typing import Dict
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.backup.config import RESTIC_DIR, RESTIC_PASSWORD
from openvair.modules.backup.adapters.restic.restic import ResticAdapter


def test_delete_backup_success(
    client: TestClient, backup_snapshot: Dict
) -> None:
    """Test successful deletion of an existing snapshot.

    Asserts:
    - 200 OK status code
    - Correct response structure
    - Success status
    - Empty error field
    """
    snapshot_id = backup_snapshot['snapshot_id']
    response = client.delete(f'/backup/{snapshot_id}')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'success'
    assert data['error'] is None

    restic_adapter = ResticAdapter(RESTIC_DIR, RESTIC_PASSWORD)
    restic_snapshots = restic_adapter.snapshots()
    assert len(restic_snapshots) == 0


def test_delete_backup_nonexistent_snapshot(
    client: TestClient, backup_repository: Path
) -> None:
    """Test handling of invalid snapshot ID.

    Asserts:
    - HTTP 500 or HTTP 200 (because of Restic logic)
    - Error message indicating snapshot not found
    """
    non_existent_id = str(uuid.uuid4())
    response = client.delete(f'/backup/{non_existent_id}')
    assert response.status_code in (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_200_OK,
    )

    data = response.json()
    assert len(data['data']['message']) > 0
    assert 'no matching id found' in data['data']['message'].lower()


def test_delete_backup_no_init_repository(
    client: TestClient, clean_backup_repository: Path
) -> None:
    """Test delete attempt from non-initialized repository.

    Asserts:
    - HTTP 500
    - Appropriate error message
    """
    backup_id = str(uuid.uuid4())
    response = client.delete(f'/backup/{backup_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    data = response.json()
    assert len(data['error']) > 0
    assert len(data['message']) > 0
    assert 'repository does not exist' in data['message'].lower()


def test_delete_backup_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized backup deletion.

    Asserts:
    - 401 Unauthorized status
    """
    backup_id = str(uuid.uuid4())
    response = unauthorized_client.delete(f'/backup/{backup_id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
