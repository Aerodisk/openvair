# noqa: D100
import time
import uuid

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.entrypoints.schemas import CreateVolume

LOG = get_logger(__name__)


def test_create_volume_success(client: TestClient, test_storage: dict) -> None:
    """Test successful volume creation."""
    volume_data = CreateVolume(
        name=f'test-volume-{uuid.uuid4().hex[:6]}',
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
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert (
        'storage' in response.text.lower()
    )  # Сообщение о несуществующем хранилище  # noqa: RUF003
