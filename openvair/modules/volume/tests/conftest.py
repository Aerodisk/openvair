# noqa: D100
from uuid import UUID, uuid4
from typing import Generator
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from openvair.main import app
from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user
from openvair.modules.volume.adapters.orm import VolumeAttachVM
from openvair.modules.volume.domain.model import VolumeFactory
from openvair.modules.volume.tests.config import settings
from openvair.modules.volume.tests.helpers import generate_volume_name
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
def client() -> Generator[TestClient, None, None]:
    """Test API client fixture."""
    with TestClient(app=app) as client:
        LOG.info('CLIENT WAS STARTS')
        yield client
        LOG.info('CLIENT WAS CLOSED')



@pytest.fixture(autouse=True, scope='session')
def mock_auth_dependency() -> None:
    """Overrides JWT dependency for tests."""
    LOG.info('Mocking authentication dependencies')
    app.dependency_overrides[oauth2schema] = lambda: 'mocked_token'
    app.dependency_overrides[get_current_user] = lambda token='mocked_token': {
        'id': str(uuid4()),
        'username': 'test_user',
        'role': 'admin',
        'token': token,
    }


@pytest.fixture(scope='session', autouse=True)
def configure_pagination() -> None:
    """Настраиваем пагинацию для тестов."""
    add_pagination(app)  # Добавляет параметры пагинации по умолчанию


def cleanup_all_volumes() -> None:  # noqa: D103
    from openvair.modules.volume.adapters.serializer import DataSerializer
    from openvair.modules.volume.service_layer.unit_of_work import (
        SqlAlchemyUnitOfWork,
    )

    LOG.info('START DELETE VOLUMES')

    unit_of_work = SqlAlchemyUnitOfWork()
    try:
        with unit_of_work as uow:
            s = uow.volumes.get_all()
            for volume_data in s:
                volume_instance = VolumeFactory().get_volume(
                    DataSerializer.to_domain(volume_data)
                )
                uow.volumes.delete(volume_data.id)
                volume_instance.delete()
                uow.commit()
                LOG.info('SUCCESS COMMIT')
        LOG.info('FINISH DELETE VOLUMES')
    except Exception as err:  # noqa: BLE001
        LOG.warning(f'Error while cleaning up volumes: {err}')


@pytest.fixture(scope='session')
def test_storage(client: TestClient) -> Generator[dict, None, None]:
    """Creates a test storage via API call and removes it after tests."""
    headers = {
        'Authorization': 'Bearer mocked_token'
    }  # 🔹 Передаём тестовый токен

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

    # 🧹 2. Теперь удаляем хранилище
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
    """Creates a test volume via API call and removes it after tests."""
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
    """Creates an attachment between volume and VM (mocked) via DB."""
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

    # Очистка после теста
    with SqlAlchemyUnitOfWork() as uow:
        db_volume = uow.volumes.get(volume_id)
        db_volume.attachments.clear()
        uow.session.query(VolumeAttachVM).filter_by(
            volume_id=volume_id
        ).delete()
        uow.commit()
