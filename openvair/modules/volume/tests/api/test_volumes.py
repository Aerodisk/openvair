  # noqa: D100
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.entrypoints.schemas import CreateVolume

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
    import time

    time.sleep(5)
