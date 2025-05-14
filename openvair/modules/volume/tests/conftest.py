"""Shared fixtures for volume integration tests.

Provides:
- `client`: FastAPI test client.
- `mock_auth_dependency`: Replaces JWT auth with mock user.
- `configure_pagination`: Enables pagination globally in tests.
- `test_storage`: Creates and removes a test storage.
- `test_volume`: Creates and deletes a volume for each test.
- `attached_volume`: Mocks a volume-to-VM attachment in the DB.

Includes:
- `cleanup_all_volumes`: Utility to delete all volumes from DB + filesystem.
"""
from uuid import UUID, uuid4
from typing import Generator
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.adapters.orm import VolumeAttachVM
from openvair.modules.volume.tests.config import settings
from openvair.modules.volume.tests.helpers import (
    cleanup_all_volumes,
    generate_volume_name,
)
from openvair.modules.volume.entrypoints.schemas import CreateVolume
from openvair.modules.storage.entrypoints.schemas import (
    CreateStorage,
    LocalFSStorageExtraSpecsCreate,
)
from openvair.modules.volume.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

LOG = get_logger(__name__)




@pytest.fixture(scope='session')
def test_storage(client: TestClient) -> Generator[dict, None, None]:
    """Creates a test storage and deletes it after session ends."""
    headers = {
        'Authorization': 'Bearer mocked_token'
    }

    storage_disk = Path(settings.storage_path)

    storage_data = CreateStorage(
        name='test-storage',
        description='Test storage for integration tests',
        storage_type='localfs',
        specs=LocalFSStorageExtraSpecsCreate(path=storage_disk, fs_type='ext4'),
    )
    response = client.post(
        '/storages/create/',
        json=storage_data.model_dump(mode='json'),
        headers=headers,
    )
    if response.status_code != status.HTTP_201_CREATED:
        message = (
            f'Failed to create storage: {response.status_code}, {response.text}'
        )
        raise RuntimeError(message)

    storage = response.json()
    yield storage
    cleanup_all_volumes()

    delete_response = client.delete(f"/storages/{storage['id']}/delete")
    if delete_response.status_code != status.HTTP_202_ACCEPTED:
        LOG.warning(
            (
                f'Failed to delete test storage: {delete_response.status_code},'
                f' {delete_response.text}'
            )
        )
    LOG.info('FINISH DELETE STORAGE')


@pytest.fixture(scope='function')
def test_volume(
    client: TestClient, test_storage: dict
) -> Generator[dict, None, None]:
    """Creates a test volume and deletes it after each test."""
    volume_data = CreateVolume(
        name=generate_volume_name(),
        description='Volume for integration tests',
        storage_id=test_storage['id'],
        format='qcow2',
        size=1024,
        read_only=False,
    )
    response = client.post(
        '/volumes/create/', json=volume_data.model_dump(mode='json')
    )
    if response.status_code != status.HTTP_200_OK:
        message = (
            f'Failed to create volume: {response.status_code}, '
            f'{response.text}'
        )
        raise RuntimeError(message)

    volume = response.json()
    yield volume

    # Cleanup: delete the volume after the test
    delete_response = client.delete(f"/volumes/{volume['id']}/")
    if delete_response.status_code != status.HTTP_202_ACCEPTED:
        LOG.warning(
            (
                f'Test volume deletion failed: {delete_response.status_code}, '
                f'{delete_response.text}'
            )
        )


@pytest.fixture(scope='function')
def attached_volume(test_volume: dict) -> Generator[dict, None, None]:
    """Creates volume-to-VM attachment (directly in DB) and removes it after test."""  # noqa: E501
    volume_id = UUID(test_volume['id'])
    vm_id = uuid4()

    with SqlAlchemyUnitOfWork() as uow:
        db_volume = uow.volumes.get(volume_id)
        attachment = VolumeAttachVM(vm_id=vm_id, volume_id=volume_id)
        db_volume.attachments.append(attachment)
        uow.session.add(attachment)
        uow.commit()

    yield {
        'volume_id': volume_id,
        'vm_id': vm_id,
    }

    with SqlAlchemyUnitOfWork() as uow:
        db_volume = uow.volumes.get(volume_id)
        db_volume.attachments.clear()
        uow.session.query(VolumeAttachVM).filter_by(
            volume_id=volume_id
        ).delete()
        uow.commit()
