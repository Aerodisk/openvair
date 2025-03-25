# noqa: D100

from typing import TYPE_CHECKING

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

if TYPE_CHECKING:
    from openvair.modules.volume.adapters.orm import Volume as ORMVolume

LOG = get_logger(__name__)


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
