# noqa: D100
import time
import uuid
from typing import TYPE_CHECKING

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.entrypoints.schemas import CreateVolume
from openvair.modules.volume.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

if TYPE_CHECKING:
    from openvair.modules.volume.adapters.orm import Volume as ORMVolume

LOG = get_logger(__name__)


def test_create_volume_success(client: TestClient, test_storage: dict) -> None:
    """Test successful volume creation."""
    volume_data = CreateVolume(
        name='test-volume',
        description='Integration test volume',
        storage_id=test_storage['id'],
        format='qcow2',
        size=1024,
        read_only=False,
    )
    response = client.post(
        '/volumes/create/', json=volume_data.model_dump(mode='json')
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert 'id' in data
    assert data['name'] == volume_data.name
    assert data['size'] == volume_data.size
    assert data['format'] == volume_data.format

    time.sleep(5)


def test_create_volume_invalid_size(
    client: TestClient, test_storage: dict
) -> None:
    """Test creation failure with invalid size (zero)."""
    volume_data = {
        'name': 'volume-invalid-size',
        'description': 'Invalid size test',
        'storage_id': test_storage['id'],
        'format': 'qcow2',
        'size': 0,  # Invalid
        'read_only': False,
    }
    response = client.post('/volumes/create/', json=volume_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_volume_without_name(
    client: TestClient, test_storage: dict
) -> None:
    """Test volume creation fails when 'name' is missing."""
    volume_data = {
        # 'name' is omitted
        'description': 'Missing name',
        'storage_id': test_storage['id'],
        'format': 'qcow2',
        'size': 1024,
        'read_only': False,
    }
    response = client.post('/volumes/create/', json=volume_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_volume_with_special_chars_in_name(
    client: TestClient, test_storage: dict
) -> None:
    """Test volume creation fails with special characters in name."""
    volume_data = {
        'name': 'invalid!name',
        'description': 'Invalid chars',
        'storage_id': test_storage['id'],
        'format': 'qcow2',
        'size': 1024,
        'read_only': False,
    }
    response = client.post('/volumes/create/', json=volume_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_volume_with_invalid_format(
    client: TestClient, test_storage: dict
) -> None:
    """Test volume creation fails with unsupported format."""
    volume_data = {
        'name': 'volume-invalid-format',
        'description': 'Unsupported format',
        'storage_id': test_storage['id'],
        'format': 'not_allowed',  # Not allowed
        'size': 1024,
        'read_only': False,
    }
    response = client.post('/volumes/create/', json=volume_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_volume_with_duplicate_name(
    client: TestClient, test_storage: dict
) -> None:
    """Test volume creation fails with duplicate name on the same storage."""
    volume_data = {
        'name': 'duplicate-volume',
        'description': 'First volume',
        'storage_id': test_storage['id'],
        'format': 'qcow2',
        'size': 1024,
        'read_only': False,
    }
    # 1. Create volume
    response_1 = client.post('/volumes/create/', json=volume_data)
    assert response_1.status_code == status.HTTP_200_OK

    # 2. Attempt to create again
    response_2 = client.post('/volumes/create/', json=volume_data)
    assert response_2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_volume_with_too_large_size(
    client: TestClient, test_storage: dict
) -> None:
    """Test creation fails if requested size exceeds available storage."""
    volume_data = {
        'name': 'too-big-volume',
        'description': 'Should fail due to size',
        'storage_id': test_storage['id'],
        'format': 'qcow2',
        'size': 100**12,  # заведомо превышает допустимое
        'read_only': False,
    }
    response = client.post('/volumes/create/', json=volume_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_volume_with_nonexistent_storage(client: TestClient) -> None:
    """Test volume creation fails if storage_id does not exist."""
    volume_data = {
        'name': 'nonexistent-storage-volume',
        'description': 'Attempt to use bad storage_id',
        'storage_id': str(uuid.uuid4()),  # Нереальный UUID
        'format': 'qcow2',
        'size': 1024,
        'read_only': False,
    }

    response = client.post('/volumes/create/', json=volume_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        'storage' in response.text.lower()
    )  # Сообщение о несуществующем хранилище  # noqa: RUF003


def test_get_all_volumes(client: TestClient, test_volume: dict) -> None:
    """Test retrieving all volumes."""
    response = client.get('/volumes/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'items' in data
    assert any(v['id'] == test_volume['id'] for v in data['items'])


def test_get_volumes_by_storage_id(
    client: TestClient, test_volume: dict
) -> None:
    """Test filtering volumes by storage_id."""
    storage_id = test_volume['storage_id']
    response = client.get(f'/volumes/?storage_id={storage_id}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(volume['storage_id'] == storage_id for volume in data['items'])


def test_get_free_volumes_only(client: TestClient, test_volume: dict) -> None:
    """Test filtering only free (unattached) volumes."""
    response = client.get('/volumes/?free_volumes=true')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(volume['id'] == test_volume['id'] for volume in data['items'])


def test_get_all_volumes_no_results(client: TestClient) -> None:
    """Test retrieving volumes when none exist."""
    response = client.get('/volumes/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['total'] == 0
    assert data['items'] == []


def test_get_volumes_with_pagination(
    client: TestClient,
    test_volume: dict,  # noqa: ARG001
) -> None:
    """Test pagination metadata in volumes list."""
    response = client.get('/volumes/?page=1&size=1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert 'page' in data
    assert 'size' in data
    assert data['page'] == 1
    assert data['size'] == 1


def test_get_volumes_with_nonexistent_storage(client: TestClient) -> None:
    """Test filtering volumes by non-existent storage_id returns empty list."""
    response = client.get(f'/volumes/?storage_id={uuid.uuid4()}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['items'] == []


def test_get_volumes_with_invalid_storage_id(client: TestClient) -> None:
    """Test invalid UUID in storage_id query param returns 422."""
    response = client.get('/volumes/?storage_id=not-a-uuid')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_volumes_with_invalid_free_volumes_param(
    client: TestClient,
) -> None:
    """Test invalid free_volumes query param returns 422."""
    response = client.get('/volumes/?free_volumes=maybe')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_existing_volume_by_id(
    client: TestClient, test_volume: dict
) -> None:
    """Test retrieving an existing volume by its ID."""
    volume_id = test_volume['id']
    response = client.get(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == volume_id
    assert data['name'] == test_volume['name']
    assert data['storage_id'] == test_volume['storage_id']


def test_get_nonexistent_volume_by_id(client: TestClient) -> None:
    """Test retrieving a volume with a valid UUID that does not exist."""
    fake_volume_id = str(uuid.uuid4())
    response = client.get(f'/volumes/{fake_volume_id}/')
    # API возвращает 200 с пустым dict — поведение зависит от реализации  # noqa: E501, RUF003, W505
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert data == {} or data.get('id') == fake_volume_id  # Допустимо пусто


def test_get_volume_with_invalid_uuid(client: TestClient) -> None:
    """Test retrieving a volume with an invalid UUID string."""
    response = client.get('/volumes/invalid-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_volume_success(client: TestClient, test_volume: dict) -> None:
    """Test successful update of volume metadata."""
    volume_id = test_volume['id']
    payload = {
        'name': 'updated-volume',
        'description': 'Updated description',
        'read_only': True,
    }
    response = client.put(f'/volumes/{volume_id}/edit/', json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['name'] == payload['name']
    assert data['description'] == payload['description']
    assert data['read_only'] is True


def test_edit_volume_with_invalid_uuid(client: TestClient) -> None:
    """Test edit attempt with invalid UUID format."""
    payload = {
        'name': 'something',
        'description': 'test',
        'read_only': False,
    }
    response = client.put('/volumes/invalid-uuid/edit/', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_volume_with_invalid_data(
    client: TestClient, test_volume: dict
) -> None:
    """Test edit attempt with invalid payload (name too short)."""
    volume_id = test_volume['id']
    payload = {
        'name': '',  # Invalid
        'description': 'Still valid',
        'read_only': False,
    }
    response = client.put(f'/volumes/{volume_id}/edit/', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_volume_when_status_not_available(
    client: TestClient, test_volume: dict
) -> None:
    """Test editing a volume with invalid status (not available)."""
    volume_id = test_volume['id']

    # 🛠 Меняем статус вручную в БД
    with SqlAlchemyUnitOfWork() as uow:
        db_volume: ORMVolume = uow.volumes.get(volume_id)
        db_volume.status = 'extending'
        uow.commit()

    payload = {
        'name': 'should-fail',
        'description': 'Trying to update',
        'read_only': False,
    }
    response = client.put(f'/volumes/{volume_id}/edit/', json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeStatusException' in response.text


def test_edit_volume_duplicate_name(
    client: TestClient, test_storage: dict
) -> None:
    """Test editing volume to use duplicate name in same storage."""
    # 1. Создаём 2 тома
    v1 = client.post(  # noqa: F841
        '/volumes/create/',
        json={
            'name': 'original-volume',
            'description': 'v1',
            'storage_id': test_storage['id'],
            'format': 'qcow2',
            'size': 1024,
            'read_only': False,
        },
    ).json()

    v2 = client.post(
        '/volumes/create/',
        json={
            'name': 'conflict-name',
            'description': 'v2',
            'storage_id': test_storage['id'],
            'format': 'qcow2',
            'size': 1024,
            'read_only': False,
        },
    ).json()

    # 2. Пытаемся дать v2 имя v1
    response = client.put(
        f"/volumes/{v2['id']}/edit/",
        json={
            'name': 'original-volume',
            'description': 'Try to rename',
            'read_only': False,
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeExistsOnStorageException' in response.text


def test_extend_volume_success(client: TestClient, test_volume: dict) -> None:
    """Test successful extension of volume size."""
    volume_id = test_volume['id']
    new_size = 2048

    response = client.post(
        f'/volumes/{volume_id}/extend/', json={'new_size': new_size}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == volume_id
    assert data['status'] == 'extending'

    time.sleep(5)
    response = client.get(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['size'] == new_size


def test_extend_volume_invalid_uuid(client: TestClient) -> None:
    """Test extending a volume with invalid UUID."""
    response = client.post(
        '/volumes/not-a-uuid/extend/',
        json={'new_size': 2048},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_extend_volume_smaller_than_current(
    client: TestClient, test_volume: dict
) -> None:
    """Test extending volume with new size <= current size."""
    volume_id = test_volume['id']
    new_size = test_volume['size']  # same size

    response = client.post(
        f'/volumes/{volume_id}/extend/',
        json={'new_size': new_size},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'ValidateArgumentsError' in response.text


def test_extend_volume_status_not_available(
    client: TestClient, test_volume: dict
) -> None:
    """Test extending a volume with invalid status (not available)."""
    volume_id = test_volume['id']
    with SqlAlchemyUnitOfWork() as uow:
        db_volume: ORMVolume = uow.volumes.get(volume_id)
        db_volume.status = 'extending'
        uow.commit()

    response = client.post(
        f'/volumes/{volume_id}/extend/',
        json={'new_size': db_volume.size + 1024},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeStatusException' in response.text
