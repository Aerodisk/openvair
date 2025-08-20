"""Integration tests for extending volumes.

Covers:
- Successful size extension of a volume.
- Input validation (invalid UUID, invalid size).
- Logical constraints (volume not in `available` status).
- Unauthorized access.
"""

from typing import TYPE_CHECKING, Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import wait_for_field_value
from openvair.modules.volume.service_layer.unit_of_work import (
    VolumeSqlAlchemyUnitOfWork,
)

if TYPE_CHECKING:
    from openvair.modules.volume.adapters.orm import Volume as ORMVolume
LOG = get_logger(__name__)


def test_extend_volume_success(client: TestClient, volume: Dict) -> None:
    """Test successful extension of volume size.

    Asserts:
    - Status is updated to 'extending', then 'available'.
    - Final size matches expected.
    """
    volume_id = volume['id']
    new_size = 2048

    response = client.post(
        f'/volumes/{volume_id}/extend/', json={'new_size': new_size}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == volume_id
    assert data['status'] == 'extending'

    wait_for_field_value(
        client, f'/volumes/{volume_id}/', 'status', 'available'
    )

    response = client.get(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['size'] == new_size


def test_extend_volume_invalid_uuid(client: TestClient) -> None:
    """Test failure on extending with invalid UUID format.

    Asserts:
    - HTTP 422.
    """
    response = client.post(
        '/volumes/not-a-uuid/extend/',
        json={'new_size': 2048},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_extend_volume_smaller_than_current(
    client: TestClient, volume: Dict
) -> None:
    """Test failure when new size is not greater than current size.

    Asserts:
    - HTTP 500 with 'ValidateArgumentsError'.
    """
    volume_id = volume['id']
    new_size = volume['size']  # same size

    response = client.post(
        f'/volumes/{volume_id}/extend/',
        json={'new_size': new_size},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'ValidateArgumentsError' in response.text


def test_extend_volume_status_not_available(
    client: TestClient, volume: Dict
) -> None:
    """Test failure when volume status is not 'available'.

    Asserts:
    - HTTP 500 with 'VolumeStatusException'.
    """
    volume_id = volume['id']
    with VolumeSqlAlchemyUnitOfWork() as uow:
        db_volume: ORMVolume = uow.volumes.get_or_fail(volume_id)
        db_volume.status = 'extending'
        uow.commit()

    response = client.post(
        f'/volumes/{volume_id}/extend/',
        json={'new_size': db_volume.size + 1024},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeStatusException' in response.text


def test_extend_volume_unauthorized(
        volume: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized request returns 401."""
    volume_id = volume['id']
    new_size = 2048

    response = unauthorized_client.post(
        f'/volumes/{volume_id}/extend/', json={'new_size': new_size}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
