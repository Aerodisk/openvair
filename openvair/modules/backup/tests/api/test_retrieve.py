# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for retrieving backup snapshots via API.

Covers:
- Successful retrieval of snapshots
- Empty repository case
- Unauthorized access
"""

from typing import Dict, List
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient


def test_get_backup_snapshots_success(
    client: TestClient, backup_repository: Path
) -> None:
    """Test successful retrieval of backup snapshots.

    Asserts:
    - Response is 200 OK
    - Correct response structure
    - List type returned
    """
    response = client.get('/backup/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'success'
    assert isinstance(data['data'], List)
    assert data['error'] is None


def test_get_backup_snapshots_with_data(
    client: TestClient, backup_snapshot: Dict
) -> None:
    """Test successful snapshot retrieval with real data structure.

    Asserts:
    - Response structure match
    - Correct path types
    - Non-empty snapshot ID
    """
    response = client.get('/backup/')
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'data' in data
    assert isinstance(data['data'], List)
    assert len(data['data']) > 0

    assert data.get('status') == 'success'
    assert data.get('error') is None

    snapshot = data['data'][0]
    expected_fields = {
        'id',
        'short_id',
        'time',
        'paths',
        'hostname',
        'username',
    }

    assert set(snapshot.keys()) == expected_fields
    assert snapshot['id'] == backup_snapshot['snapshot_id']

    assert 'paths' in snapshot
    assert isinstance(snapshot['paths'], List)
    assert len(snapshot['paths']) > 0
    assert all(isinstance(path, str) for path in snapshot['paths'])
    assert all(path.startswith('/') for path in snapshot['paths'])


def test_get_backup_snapshots_empty_repository(
    client: TestClient, backup_repository: Path
) -> None:
    """Test empty repository response.

    Asserts:
    - Empty list in data field
    - Success status
    """
    response = client.get('/backup/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'success', 'data': [], 'error': None}


def test_get_backup_snapshots_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test authentication requirements.

    Asserts:
    - 401 status for unauthenticated requests
    """
    response = unauthorized_client.get('/backup/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
