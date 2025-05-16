# noqa: D100
from uuid import uuid4
from typing import Generator
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from openvair.main import app
from openvair.libs.log import get_logger
from openvair.libs.testing_utils import (
    create_resource,
    delete_resource,
    cleanup_all_volumes,
    generate_test_entity_name,
)
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user
from openvair.modules.volume.tests.config import settings
from openvair.modules.volume.entrypoints.schemas import CreateVolume
from openvair.modules.storage.entrypoints.schemas import (
    CreateStorage,
    LocalFSStorageExtraSpecsCreate,
)

LOG = get_logger(__name__)


@pytest.fixture(scope='session')
def client() -> Generator[TestClient, None, None]:
    """Creates FastAPI TestClient with app instance for API testing."""
    with TestClient(app=app) as client:
        LOG.info('CLIENT WAS STARTS')
        yield client
        LOG.info('CLIENT WAS CLOSED')


@pytest.fixture(scope='session')
def unauthorized_client() -> Generator[TestClient, None, None]:
    """TestClient without mocked auth for unauthorized access tests."""
    with TestClient(app=app) as client:
        app.dependency_overrides[get_current_user] = lambda: None
        yield client


@pytest.fixture(autouse=True, scope='session')
def mock_auth_dependency() -> None:
    """Overrides real JWT authentication with a mocked test user."""
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
    """Registers pagination support in the test app (FastAPI-pagination)."""
    add_pagination(app)


@pytest.fixture(scope='session')
def test_storage(client: TestClient) -> Generator[dict, None, None]:
    """Creates a test storage and deletes it after session ends."""
    headers = {'Authorization': 'Bearer mocked_token'}

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
        name=generate_test_entity_name('volume'),
        description='Volume for integration tests',
        storage_id=test_storage['id'],
        format='qcow2',
        size=1024,
        read_only=False,
    ).model_dump(mode='json')
    volume = create_resource(client, '/volumes/create/', volume_data, 'volume')

    yield volume

    delete_resource(client, '/volumes', volume['id'], 'volume')
