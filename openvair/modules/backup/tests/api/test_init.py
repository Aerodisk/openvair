"""Integration tests for initialising backup repository via API.

Covers:
- Successful repository initialization.
- Logical errors (e.g. double repository initialization).
- Unauthorized access.
"""

from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient


def test_init_backup_repository_success(
    client: TestClient, clean_backup_repository: Path
) -> None:
    """Test repository initialization.

    Asserts:
    - Response is 200 OK.
    - Returned fields match request.
    - Backup repository initialized.
    """
    response = client.post('/backup/repository')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] == 'success'

    assert (clean_backup_repository / 'config').exists()


def test_init_backup_repository_double(
    client: TestClient, clean_backup_repository: Path
) -> None:
    """Test of double initialization.

    Asserts:
    - Response is 200 OK after the first request.
    - Second request returns HTTP 500.
    - Returned fields match request.
    - Backup repository initialized.
    """
    response = client.post('/backup/repository')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] == 'success'

    response = client.post('/backup/repository')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_data = response.json()
    assert 'config file already exists' in error_data['message']

    assert (clean_backup_repository / 'config').exists()


def test_init_backup_repository_unauthorized(
    unauthorized_client: TestClient, clean_backup_repository: Path
) -> None:
    """Test unauthorized request of repository initialization.

    Asserts:
    - HTTP 401 - unauthorized access.
    """
    response = unauthorized_client.post('/backup/repository')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert not ((clean_backup_repository / 'config').exists())
