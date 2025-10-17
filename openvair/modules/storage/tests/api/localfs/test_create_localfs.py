"""Integration tests for storage creation endpoints (localfs).

Covers:
- Successful storage creation.
- Validation errors (missing fields, invalid name, specs, etc.).
- Logical errors (nonexistent path).
- Unauthorized access.
"""

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import (
    wait_for_field_value,
    generate_test_entity_name,
)
from openvair.libs.testing.config import storage_settings


def test_create_storage_localfs_success(
    client: TestClient
) -> None:
    """Test successful localfs storage creation."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Valid localfs storage',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    storage_id = data['id']
    assert data['name'] == storage_data['name']
    assert data['storage_type'] == 'localfs'
    assert data['status'] == 'new'

    wait_for_field_value(
        client,
        f'/storages/{storage_id}/',
        'status',
        'available',
    )


def test_create_storage_missing_name(
    client: TestClient
) -> None:
    """Test failure when name is missing."""
    storage_data = {
        'description': 'Missing name test',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'name' in response.text


def test_create_storage_missing_storage_type(
    client: TestClient
) -> None:
    """Test failure when storage_type is missing."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Missing storage_type test',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'storage_type' in response.text.lower()


def test_create_storage_missing_specs(
    client: TestClient
) -> None:
    """Test failure when specs are missing."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Missing specs test',
        'storage_type': 'localfs',
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'specs' in response.text.lower()


def test_create_storage_invalid_name(client: TestClient) -> None:
    """Test failure with invalid characters in name."""
    storage_data = {
        'name': 'invalid!name@',
        'description': 'Invalid name test',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'name' in response.text


def test_create_storage_invalid_fs_type(
    client: TestClient
) -> None:
    """Test failure with invalid filesystem type."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Invalid FS type test',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': 'invalid_fs',
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'fs_type' in response.text.lower()
    assert 'xfs' in response.text.lower()
    assert 'ext4' in response.text.lower()


def test_create_storage_invalid_description_chars(
    client: TestClient
) -> None:
    """Test failure with invalid characters in description."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Invalid@description!',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'description' in response.text.lower()
    assert 'special characters' in response.text.lower()


def test_create_storage_nonexistent_path(
    client: TestClient
) -> None:
    """Test failure with nonexistent local path."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Nonexistent path test',
        'storage_type': 'localfs',
        'specs': {
            'path': '/nonexistent/path',
            'fs_type': 'ext4',
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'path' in response.text.lower()


def test_create_storage_duplicate_path(
    client: TestClient
) -> None:
    """Test failure when storage path already exists."""
    storage_data1 = {
        'name': 'storage-path-test-1',
        'description': 'First storage',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response1 = client.post('/storages/create/', json=storage_data1)
    assert response1.status_code == status.HTTP_201_CREATED

    storage_data2 = {
        'name': 'storage-path-test-2',
        'description': 'Second storage',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': 'ext4',
        },
    }

    response2 = client.post('/storages/create/', json=storage_data2)
    assert response2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'already exists' in response2.text.lower()


def test_create_storage_unauthorized(
    unauthorized_client: TestClient
) -> None:
    """Test unauthorized storage creation."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Unauthorized test',
        'storage_type': 'localfs',
        'specs': {
            'path': str(storage_settings.storage_path),
            'fs_type': storage_settings.storage_fs_type,
        },
    }

    response = unauthorized_client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
