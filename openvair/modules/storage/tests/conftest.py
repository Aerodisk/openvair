"""Fixtures for storage integration tests."""

from typing import Any, Dict, Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    create_resource,
    delete_resource,
    cleanup_partitions,
    cleanup_all_volumes,
    get_disk_partitions,
    cleanup_all_storages,
    wait_for_field_value,
    cleanup_all_templates,
    generate_test_entity_name,
)
from openvair.libs.testing.config import storage_settings
from openvair.modules.template.shared.enums import TemplateStatus
from openvair.modules.volume.entrypoints.schemas import CreateVolume
from openvair.modules.storage.entrypoints.schemas import CreateLocalPartition
from openvair.modules.volume.service_layer.services import VolumeStatus
from openvair.modules.storage.service_layer.services import StorageStatus
from openvair.modules.template.entrypoints.schemas.requests import (
    RequestCreateTemplate,
)

LOG = get_logger(__name__)


@pytest.fixture(scope='function')
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
            target_disk_path = disk['parent']
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


@pytest.fixture(scope='function')
def nfs_storage(client: TestClient) -> Generator[Dict, None, None]:
    """Creates a test NFS storage and deletes it after test."""
    cleanup_all_storages()

    storage_data = {
        'name': generate_test_entity_name('nfs_storage'),
        'description': 'Test NFS storage for integration tests',
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': str(storage_settings.storage_nfs_path),
            'mount_version': '4',
        },
    }

    nfs_storage_data = create_resource(
        client,
        '/storages/create/',
        storage_data,
        'nfs_storage',
    )

    wait_for_field_value(
        client=client,
        path=f"/storages/{nfs_storage_data['id']}/",
        field='status',
        expected=StorageStatus.available.name,
    )

    yield nfs_storage_data

    cleanup_all_volumes()
    cleanup_all_templates()

    delete_resource(client, '/storages', nfs_storage_data['id'], 'nfs_storage')


@pytest.fixture(scope='function')
def nfs_volume(
    client: TestClient, nfs_storage: Dict
) -> Generator[Dict, None, None]:
    """Creates a test volume on NFS storage and deletes it after each test."""
    volume_data = CreateVolume(
        name=generate_test_entity_name('volume'),
        description='Volume for integration tests on NFS storage',
        storage_id=nfs_storage['id'],
        format='qcow2',
        size=1024,  # 1GB
        read_only=False,
    ).model_dump(mode='json')

    volume = create_resource(
        client, '/volumes/create/', volume_data, 'nfs_volume'
    )

    wait_for_field_value(
        client=client,
        path=f'/volumes/{volume["id"]}/',
        field='status',
        expected=VolumeStatus.available.name,
    )

    yield volume

    delete_resource(client, '/volumes', volume['id'], 'nfs_volume')


@pytest.fixture(scope='function')
def nfs_template(
    client: TestClient, nfs_storage: Dict, nfs_volume: Dict
) -> Generator[Dict, None, None]:
    """Creates a test template on NFS storage and deletes it after each test."""
    template_data = RequestCreateTemplate(
        base_volume_id=nfs_volume['id'],
        name=generate_test_entity_name('template'),
        description='Template for integration tests on NFS storage',
        storage_id=nfs_storage['id'],
        is_backing=False,
    ).model_dump(mode='json')

    template = create_resource(
        client, '/templates/', template_data, 'nfs_template'
    )['data']

    wait_for_field_value(
        client=client,
        path=f"/templates/{template['id']}/",
        field='status',
        expected=TemplateStatus.AVAILABLE,
    )

    yield template

    delete_resource(client, '/templates', template['id'], 'nfs_template')
