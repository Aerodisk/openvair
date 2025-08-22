"""Integration tests for image upload API endpoint.

This test suite covers:
- Successful image uploads with and without descriptions.
- Rejection of unauthorized upload attempts.
- Validation for missing required fields.
- Handling of uploads with invalid storage IDs and file formats.
- Edge cases including very long names/descriptions and duplicate uploads.
- Verification that temporary files are cleaned up after upload attempts.
"""

import time
import uuid
from typing import Dict
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.config import TMP_DIR
from openvair.libs.testing.utils import (
    generate_image_name,
    generate_random_string,
    generate_test_entity_name,
)
from openvair.libs.testing.config import image_settings

image_path = image_settings.image_path

@pytest.mark.parametrize('description', [True, False])
def test_upload_image_success(
    client: TestClient,
    storage: Dict,
    *,
    description: bool,
) -> None:
    """Test successful upload_image with and without description."""
    desc = ''
    if description:
        desc = f'&description{generate_random_string(10)}'
    storage_id = storage['id']
    name = generate_image_name()
    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}{desc}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['name'] == name
    assert data['storage_id'] == storage_id


def test_upload_image_unauthorized(
    unauthorized_client: TestClient,
    storage: Dict,
) -> None:
    """Test unauthorized request returns 401."""
    storage_id = storage['id']
    name = generate_image_name()
    with image_path.open("rb") as file:
        response = unauthorized_client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'missing_field', ['name', 'storage_id']
)
def test_upload_image_missing_field(
    client: TestClient,
    missing_field: str,
    storage: Dict,
) -> None:
    """Test that missing required fields result in HTTP 422."""
    storage_id = f"storage_id={storage['id']}"
    name = f'name={generate_image_name()}'
    field = name
    if missing_field == 'name':
        field = storage_id
    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?{field}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_no_image(
    client: TestClient,
    storage: Dict,
) -> None:
    """Test no upload file returns HTTP 422."""
    storage_id = storage['id']
    name = generate_image_name()
    response = client.post(
        f"/images/upload/?storage_id={storage_id}&name={name}",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_wrong_file_formate(
    client: TestClient,
    storage: Dict
) -> None:
    """Test wrong file formate returns HTTP 422."""
    storage_id = storage['id']
    name = generate_image_name()

    file_name = (f'/opt/aero/openvair/openvair/modules/image/tests/'
                 f'{generate_test_entity_name("image_file")}')
    file_path = Path(file_name)
    file_path.touch()
    with file_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    file_path.unlink()
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_with_wrong_storage_id(
    client: TestClient
) -> None:
    """Test upload with nonexistent storage_id returns 500."""
    storage_id = str(uuid.uuid4())
    name = generate_image_name()
    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.parametrize('description', [True, False])
def test_upload_image_long_name(
    client: TestClient,
    *,
    description: bool,
    storage: Dict
) -> None:
    """Test upload with long name or description returns 500."""
    storage_id = storage['id']
    name = generate_image_name()
    desc = ''
    if description:
        desc = f'&description={generate_random_string(41)}'
    else:
        name = f'{generate_random_string(37)}.iso'
    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}{desc}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_upload_image_wrong_storage(
    client: TestClient
) -> None:
    """Test storage not uuid returns 422."""
    storage_id = "storage"
    name = generate_image_name()
    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_with_excisting_name(
    client: TestClient,
    storage: Dict,
) -> None:
    """Test uploading image with the same name twice returns 500"""
    storage_id = storage['id']
    name = generate_image_name()
    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    assert response.status_code == status.HTTP_200_OK

    with image_path.open("rb") as file:
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    time.sleep(3)
    file_path = Path(TMP_DIR, name)
    assert Path.is_file(file_path) is False
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
