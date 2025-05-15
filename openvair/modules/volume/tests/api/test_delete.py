"""Integration tests for volume deletion.

Covers:
- Successful deletion of a volume.
- Deletion errors due to:
    - invalid UUID,
    - non-deletable status (e.g. `extending`),
    - existing VM attachments.
"""

from typing import TYPE_CHECKING

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.tests.test_utils import wait_for_status
from openvair.modules.volume.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

if TYPE_CHECKING:
    from openvair.modules.volume.adapters.orm import Volume as ORMVolume

LOG = get_logger(__name__)


def test_delete_volume_success(client: TestClient, test_volume: dict) -> None:
    """Test successful deletion of a volume in 'available' state."""
    volume_id = test_volume['id']
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


def test_delete_volume_invalid_status(
    client: TestClient, test_volume: dict
) -> None:
    """Test failure when trying to delete a volume not in 'available' state.

    Manually sets status to 'extending'.

    Asserts:
    - HTTP 500 with 'VolumeStatusException'.
    """
    wait_for_status(
        client,
        test_volume['id'],
        'available',
    )
    with SqlAlchemyUnitOfWork() as uow:
        volume: ORMVolume = uow.volumes.get(test_volume['id'])
        volume.status = 'extending'
        uow.commit()

    response = client.delete(f"/volumes/{test_volume['id']}/")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeStatusException' in response.text


def test_delete_volume_with_attachment(
    client: TestClient, attached_volume: dict
) -> None:
    """Test failure when volume is attached to a VM.

    Asserts:
    - HTTP 500 with 'VolumeHasAttachmentError'.
    """
    volume_id = attached_volume['volume_id']
    response = client.delete(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeHasAttachmentError' in response.text
