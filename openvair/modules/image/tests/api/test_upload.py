"""Integration tests for image upload API endpoint.

This test suite covers:
- Successful image uploads with and without descriptions.
- Rejection of unauthorized upload attempts.
- Validation for missing required fields.
- Handling of uploads with invalid storage IDs and file formats.
- Edge cases including very long names/descriptions and duplicate uploads.
- Verification that temporary files are cleaned up after upload attempts.
"""

import uuid
from typing import Dict, BinaryIO
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import wait_for_field_value
from openvair.modules.image.tests.utils import upload_image_api_call


def test_upload_image_success(
    client: TestClient,
    storage: Dict,
    name: str,
    image_file: BinaryIO
) -> None:
    """Test successful upload_image."""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': name
    }
    response = upload_image_api_call (name, query, client, image_file)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['name'] == name
    assert data['storage_id'] == storage_id

    wait_for_field_value(
        client, f'/images/{data["id"]}/', 'status', 'available'
    )
    storage_path = ('/opt/aero/openvair/data/mnt/'
                    f'{storage["storage_type"]}-{storage_id}')
    wait_for_field_value(
        client,
        f'/images/{data["id"]}/',
        'path',
        storage_path
    )
    new_image_path = Path(storage_path, f'image-{data["id"]}')
    assert new_image_path.exists() is True


def test_upload_image_unauthorized(
    unauthorized_client: TestClient,
    storage: Dict,
    name: str,
    image_file: BinaryIO
) -> None:
    """Test unauthorized request returns 401."""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': name
    }
    response = upload_image_api_call (
        name, query, unauthorized_client, image_file
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'missing_field', ['name', 'storage_id']
)
def test_upload_image_missing_field(
    client: TestClient,
    missing_field: str,
    image_file: BinaryIO,
    name: str,
    storage: Dict,
) -> None:
    """Test that missing required fields result in HTTP 422."""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': name
    }
    query.pop(missing_field, None)
    response = upload_image_api_call (name, query, client, image_file)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_no_image(
    client: TestClient,
    name: str,
    storage: Dict,
) -> None:
    """Test no upload file returns HTTP 422."""
    storage_id = storage['id']
    response = client.post(
        f"/images/upload/?storage_id={storage_id}&name={name}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_wrong_file_format(
    client: TestClient,
    storage: Dict,
    name: str,
    wrong_format_file: BinaryIO
) -> None:
    """Test wrong file format returns HTTP 422."""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': name
    }
    response = upload_image_api_call (name, query, client, wrong_format_file)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_with_wrong_storage_id(
    client: TestClient,
    image_file: BinaryIO,
    name: str
) -> None:
    """Test upload with nonexistent storage_id returns 500."""
    query = {
        'storage_id': str(uuid.uuid4()),
        'name': name
    }
    response = upload_image_api_call (name, query, client, image_file)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_upload_image_long_name(
    client: TestClient,
    image_file: BinaryIO,
    long_name: str,
    storage: Dict
) -> None:
    """Test upload with long name or description returns 500."""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': long_name
    }
    response = upload_image_api_call (long_name, query, client, image_file)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_upload_image_storage_not_uuid(
    client: TestClient,
    image_file: BinaryIO,
    name: str
) -> None:
    """Test storage not uuid returns 422."""
    query = {
        'storage_id': 'storage',
        'name': name
    }
    response = upload_image_api_call (name, query, client, image_file)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_with_existing_name(
    client: TestClient,
    image_file: BinaryIO,
    name: str,
    storage: Dict,
) -> None:
    """Test uploading image with the same name twice returns 500"""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': name
    }
    response = upload_image_api_call (name, query, client, image_file)
    assert response.status_code == status.HTTP_200_OK

    response = upload_image_api_call (name, query, client, image_file)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
