"""Integration tests for volume deletion.

Covers:
- Successful deletion of a volume.
- Deletion errors due to:
    - invalid UUID,
    - non-deletable status (e.g. `extending`),
    - existing VM attachments.
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


def test_delete_volume_success(client: TestClient, volume: Dict) -> None:
    """Test successful deletion of a volume in 'available' state."""
    volume_id = volume['id']
    response = client.delete(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == volume_id
    assert data['status'] == 'deleting'


def test_delete_volume_invalid_uuid(client: TestClient) -> None:
    """Test deletion attempt using invalid UUID format.

    Asserts:
    - HTTP 422 Unprocessable Entity.
    """
    response = client.delete('/volumes/not-a-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_volume_invalid_status(client: TestClient, volume: Dict) -> None:
    """Test failure when trying to delete a volume not in 'available' state.

    Manually sets status to 'extending'.

    Asserts:
    - HTTP 500 with 'VolumeStatusException'.
    """
    wait_for_field_value(
        client, f'/volumes/{volume["id"]}/', 'status', 'available'
    )

    with VolumeSqlAlchemyUnitOfWork() as uow:
        orm_volume: ORMVolume = uow.volumes.get_or_fail(volume['id'])
        orm_volume.status = 'extending'
        uow.commit()

    response = client.delete(f"/volumes/{volume['id']}/")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeStatusException' in response.text


def test_delete_volume_with_attachment(
    client: TestClient, attached_volume: Dict
) -> None:
    """Test failure when volume is attached to a VM.

    Asserts:
    - HTTP 500 with 'VolumeHasAttachmentError'.
    """
    volume_id = attached_volume['volume_id']
    response = client.delete(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeHasAttachmentError' in response.text


def test_delete_volume_unauthorized(
    volume: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized request returns 401."""
    volume_id = volume['id']
    response = unauthorized_client.delete(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
