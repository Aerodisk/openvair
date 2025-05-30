"""Integration tests for editing volumes.

Covers:
- Successful update of volume metadata (name, description, read-only).
- Validation errors (invalid UUID, invalid input data).
- Logical constraints (invalid status, duplicate name).
"""

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


def test_edit_volume_success(client: TestClient, volume: dict) -> None:
    """Test successful metadata update for a volume."""
    volume_id = volume['id']
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
    """Test failure when editing volume with invalid UUID.

    Asserts:
    - HTTP 422 Unprocessable Entity.
    """
    payload = {
        'name': 'something',
        'description': 'test',
        'read_only': False,
    }
    response = client.put('/volumes/invalid-uuid/edit/', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_volume_with_invalid_data(
    client: TestClient, volume: dict
) -> None:
    """Test failure when name field is empty.

    Asserts:
    - HTTP 422 validation error.
    """
    volume_id = volume['id']
    payload = {
        'name': '',  # Invalid
        'description': 'Still valid',
        'read_only': False,
    }
    response = client.put(f'/volumes/{volume_id}/edit/', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_volume_when_status_not_available(
    client: TestClient, volume: dict
) -> None:
    """Test failure when editing a volume with non-available status.

    Status is set manually to 'extending'.

    Asserts:
    - HTTP 500 with 'VolumeStatusException'.
    """
    volume_id = volume['id']

    # Change manual DB status
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


def test_edit_volume_duplicate_name(client: TestClient, storage: dict) -> None:
    """Test failure when renaming volume to name that already exists in storage.

    Asserts:
    - HTTP 500 with 'VolumeExistsOnStorageException'.
    """
    # 1. creates 2 volumes
    v1 = client.post(  # noqa: F841
        '/volumes/create/',
        json={
            'name': 'original-volume',
            'description': 'v1',
            'storage_id': storage['id'],
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
            'storage_id': storage['id'],
            'format': 'qcow2',
            'size': 1024,
            'read_only': False,
        },
    ).json()

    # 2. try to set the name for v2 as for v1.
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
