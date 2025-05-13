"""Integration tests for volume creation.

Covers:
- Successful volume creation.
- Validation errors (e.g. missing fields, invalid size, format, name).
- Logical errors (duplicate name, nonexistent storage, oversized request).
"""

import uuid

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.tests.helpers import (
    wait_for_status,
    generate_volume_name,
)
from openvair.modules.volume.entrypoints.schemas import CreateVolume

LOG = get_logger(__name__)


def test_create_volume_success(client: TestClient, test_storage: dict) -> None:
    """Test successful volume creation.

    Asserts:
    - Response is 200 OK.
    - Returned fields match request.
    - Volume reaches 'available' status.
    """
    volume_data = CreateVolume(
        name=generate_volume_name(),
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

    wait_for_status(
        client,
        data['id'],
        'available',
    )


def test_create_volume_invalid_size(
    client: TestClient, test_storage: dict
) -> None:
    """Test creation failure with invalid size (0 bytes).

    Asserts:
    - HTTP 422 due to failed validation.
    """
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
    """Test volume creation fails if 'name' is missing.

    Asserts:
    - HTTP 422 due to required field missing.
    """
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
    """Test failure on invalid characters in volume name.

    Asserts:
    - HTTP 422 due to invalid format.
    """
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
    """Test failure when volume format is not allowed.

    Asserts:
    - HTTP 422 due to unsupported format.
    """
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
    """Test failure when creating a volume with duplicate name in same storage.

    Asserts:
    - Second request returns HTTP 500.
    """
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
    """Test failure when requested size exceeds storage capacity.

    Asserts:
    - HTTP 500 due to internal size check failure.
    """
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
    """Test failure when storage_id is not found in database.

    Asserts:
    - HTTP 500 with 'storage' mentioned in response.
    """
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
