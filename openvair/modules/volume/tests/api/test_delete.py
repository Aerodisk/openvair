# noqa: D100
import time
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


def test_delete_volume_success(client: TestClient, test_volume: dict) -> None:
    """Test successful deletion of an available volume."""
    volume_id = test_volume['id']
    response = client.delete(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == volume_id
    assert data['status'] == 'deleting'


def test_delete_volume_invalid_uuid(client: TestClient) -> None:
    """Test deletion with invalid UUID format."""
    response = client.delete('/volumes/not-a-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_volume_invalid_status(
    client: TestClient, test_volume: dict
) -> None:
    """Test deletion fails when volume is not in deletable status."""
    time.sleep(3)
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
    """Test deletion fails when volume has attachments."""
    volume_id = attached_volume['volume_id']
    response = client.delete(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'VolumeHasAttachmentError' in response.text
