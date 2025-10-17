"""Fixtures for storage integration tests."""

from typing import Any, Dict, Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    create_resource,
    cleanup_partitions,
    get_disk_partitions,
    cleanup_all_storages,
)
from openvair.libs.testing.config import storage_settings
from openvair.modules.storage.entrypoints.schemas import CreateLocalPartition

LOG = get_logger(__name__)


@pytest.fixture(scope='function', autouse=True)
def cleanup_storages() -> Generator[None, Any, None]:
    """Cleanup all storages before and after test"""
    cleanup_all_storages()
    yield
    cleanup_all_storages()


@pytest.fixture(scope='function')
def target_disk_path(client: TestClient) -> Generator[str, Any, None]:
    """Target disk path with cleanup new partitions after the test."""
    disks_response = client.get('/storages/local-disks/')
    disks_data = disks_response.json()
    target_disk_path = ''
    for disk in disks_data['disks']:
        if disk['path'] == str(storage_settings.storage_path):
            if disk.get('parent'):
                target_disk_path = disk['parent']
            else:
                target_disk_path = disk['path']
            break

    pre_existing_partitions = get_disk_partitions(target_disk_path)

    yield target_disk_path

    all_partitions = get_disk_partitions(target_disk_path)
    new_partitions = [
        p for p in all_partitions if p not in pre_existing_partitions
    ]
    if new_partitions:
        cleanup_partitions(target_disk_path, new_partitions)


@pytest.fixture(scope='function')
def local_partition(
    client: TestClient, target_disk_path: str
) -> Generator[Dict, Any, None]:
    """Creates new local partition on target disk"""
    partition_data = CreateLocalPartition(
        local_disk_path=Path(target_disk_path),
        storage_type='local_partition',
        size_value=10 * 1000 * 1000,  # 10 MB
        size_unit='B',
    ).model_dump(mode='json')

    partition = create_resource(
        client,
        '/storages/local-disks/create_partition/',
        partition_data,
        'local_partition',
    )

    yield partition
