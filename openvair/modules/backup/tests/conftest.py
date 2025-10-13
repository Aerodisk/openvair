"""Integration test fixtures for backup module.

Provides:
- `clean_backup_repository`: Creates backup repository and cleans up after test.
- `backup_repository`: Initializes and cleans up test backup repository.
- `backup_snapshot`: Creates a test backup snapshot and cleans up after test.
"""

import shutil
from pathlib import Path
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import create_resource, delete_resource
from openvair.modules.backup.config import RESTIC_DIR


@pytest.fixture(scope='function')
def clean_backup_repository() -> Generator[Path, None, None]:
    """Creates backup repository and cleans up before and after test."""
    repo_path = Path(RESTIC_DIR)

    if repo_path.exists():
        shutil.rmtree(repo_path, ignore_errors=True)

    repo_path.mkdir(parents=True, exist_ok=True)

    yield repo_path

    if repo_path.exists():
        shutil.rmtree(repo_path, ignore_errors=True)


@pytest.fixture(scope='function')
def backup_repository(
    client: TestClient,
    clean_backup_repository: Path,
) -> Generator[Path, None, None]:
    """Creates and initializes a backup repository and cleans up after test.

    Requires:
    - Created clean repository path (clean_backup_repository fixture)
    """
    repo_path = clean_backup_repository

    create_resource(client, '/backup/repository', {}, 'backup_repository')

    yield repo_path


@pytest.fixture(scope='function')
def backup_snapshot(
    client: TestClient,
    backup_repository: dict,  # noqa: ARG001 because of fixture using
) -> Generator[dict, None, None]:
    """Creates a backup snapshot, wait for creation and cleans up after test.

    Requires:
    - Initialized backup repository (backup_repository fixture)
    """
    snapshot = create_resource(client, '/backup', {}, 'backup_snapshot')['data']

    yield snapshot

    delete_resource(
        client, '/backup', snapshot['snapshot_id'], 'backup_snapshot'
    )
