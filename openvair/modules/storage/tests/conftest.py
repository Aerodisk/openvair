"""Fixtures for storage integration tests."""
from typing import Any, Dict, Generator
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    create_resource,
    cleanup_all_storages,
)
from openvair.modules.storage.entrypoints.schemas import CreateLocalPartition

LOG = get_logger(__name__)


@pytest.fixture(scope='function')
def cleanup_storages() -> Generator[None, Any, None]:
    """Cleanup all storages before and after test"""
    cleanup_all_storages()
    yield
    cleanup_all_storages()


@pytest.fixture(scope='function')
def target_disk_path(client: TestClient) -> Generator[str, Any, None]:
    """Gets target disk path for the local partition creation"""
    disks_response = client.get('/storages/local-disks/')
    disks_data = disks_response.json()
    target_disk = None
    for disk in disks_data['disks']:
        if disk['parent'] is None and disk['type'] == 'disk':
            target_disk = disk
            break
    if not target_disk:
        pytest.skip("No suitable disk for partition creation test")
    yield target_disk['path']


@pytest.fixture(scope='function')
def local_partition(
        client: TestClient, target_disk_path: str
) -> Generator[Dict, Any, None]:
    """Creates new local partition on target disk"""
    partition_data = CreateLocalPartition(
        local_disk_path=Path(target_disk_path),
        storage_type='local_partition',
        size_value=10*1000*1000,  # 10 MB
        size_unit='B',
    ).model_dump(mode='json')

    partition = create_resource(
        client,
        '/storages/local-disks/create_partition/',
        partition_data,
        'local_partition'
    )

    yield partition

    partition_number = partition["path"].replace(target_disk_path, "")
    delete_data = {
        "storage_type": "local_partition",
        "local_disk_path": target_disk_path,
        "partition_number": partition_number
    }

    delete_response = client.request(
        'DELETE',
        '/storages/local-disks/delete_partition/',
        json=delete_data
    )
    if delete_response.status_code != status.HTTP_200_OK:
        LOG.warning(
            (
                f'Failed to delete test local partition: '
                f'{delete_response.status_code}, '
                f'{delete_response.text}'
            )
        )
