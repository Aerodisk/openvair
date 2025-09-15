# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for storage creation (NFS).

Covers:
- Successful NFS storage creation.
- Validation errors (invalid IP, path, mount version, etc.).
- Logical errors (duplicate name).
- Unauthorized access.
"""

from typing import Dict, cast

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import (
    wait_for_field_value,
    generate_test_entity_name,
)
from openvair.libs.testing.config import storage_settings


def test_create_storage_nfs_success(
    client: TestClient, cleanup_storages: None
) -> None:
    """Test successful NFS storage creation."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Valid NFS storage',
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': str(storage_settings.storage_nfs_path),
            'mount_version': '4',
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['name'] == storage_data['name']
    assert data['storage_type'] == 'nfs'
    assert data['status'] == 'new'

    storage_id = data['id']
    wait_for_field_value(
        client, f'/storages/{storage_id}', 'status', 'available'
    )

    response = client.get(f'/storages/{storage_id}')
    storage_data = response.json()
    size = cast(int, storage_data['size'])
    storage_extra_specs = cast(
        Dict[str, str], storage_data['storage_extra_specs']
    )
    assert size > 0
    assert storage_extra_specs['ip'] == str(storage_settings.storage_nfs_ip)
    assert storage_extra_specs['path'] == str(storage_settings.storage_nfs_path)


def test_create_storage_nfs_invalid_ip(
    client: TestClient, cleanup_storages: None
) -> None:
    """Test failure with invalid IP address."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Invalid IP test',
        'storage_type': 'nfs',
        'specs': {
            'ip': 'invalid_ip',
            'path': str(storage_settings.storage_nfs_path),
            'mount_version': '4',
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'ip' in response.text.lower()


def test_create_storage_nfs_invalid_mount_version(
    client: TestClient, cleanup_storages: None
) -> None:
    """Test failure with invalid mount version."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Invalid mount version test',
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': '/mnt/nfs_share',
            'mount_version': '5',
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'mount_version' in response.text.lower()
    assert '3' in response.text and '4' in response.text


def test_create_storage_nfs_invalid_path(
    client: TestClient, cleanup_storages: None
) -> None:
    """Test failure with invalid path characters."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'description': 'Invalid path test',
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': '/invalid@path!',
            'mount_version': '4',
        },
    }

    response = client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'path' in response.text.lower()


def test_create_storage_nfs_missing_required_fields(
    client: TestClient, cleanup_storages: None
) -> None:
    """Test failure when required fields are missing."""
    test_cases = [
        {
            'description': 'Missing IP test',
            'specs': {
                'path': str(storage_settings.storage_nfs_path),
                'mount_version': '4',
            },
        },
        {
            'description': 'Missing path test',
            'specs': {
                'ip': str(storage_settings.storage_nfs_ip),
                'mount_version': '4',
            },
        },
    ]

    for test_case in test_cases:
        storage_data = {
            'name': generate_test_entity_name('storage'),
            'description': test_case['description'],
            'storage_type': 'nfs',
            'specs': test_case['specs'],
        }
        response = client.post('/storages/create/', json=storage_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_storage_nfs_duplicate_name(
    client: TestClient, cleanup_storages: None
) -> None:
    """Test failure with duplicate storage name."""
    storage_data1 = {
        'name': 'duplicate-test',
        'description': 'First storage',
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': str(storage_settings.storage_nfs_path),
        },
    }

    response1 = client.post('/storages/create/', json=storage_data1)
    assert response1.status_code == status.HTTP_201_CREATED
    data = response1.json()
    storage_id = data['id']
    wait_for_field_value(
        client, f'/storages/{storage_id}', 'status', 'available'
    )

    storage_data2 = {
        'name': 'duplicate-test',
        'description': 'Second storage',
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': str(storage_settings.storage_nfs_path),
        },
    }

    response2 = client.post('/storages/create/', json=storage_data2)
    assert response2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'storageexistserror' in response2.text.lower()


def test_create_storage_nfs_unauthorized(
    unauthorized_client: TestClient, cleanup_storages: None
) -> None:
    """Test unauthorized NFS storage creation."""
    storage_data = {
        'name': generate_test_entity_name('storage'),
        'storage_type': 'nfs',
        'specs': {
            'ip': str(storage_settings.storage_nfs_ip),
            'path': str(storage_settings.storage_nfs_path),
        },
    }

    response = unauthorized_client.post('/storages/create/', json=storage_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
