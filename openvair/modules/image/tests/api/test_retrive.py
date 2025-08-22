"""Integration tests for image retrieval API endpoints.

This test suite covers:
- Successful retrieval of individual images and lists of images.
- Retrieval with and without filtering by storage ID.
- Handling unauthorized access attempts.
- Validation of UUID formats in image and storage IDs.
- Behavior when fetching images or storages that do not exist.
"""

import uuid
from typing import Dict

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_get_image_success(
    client: TestClient,
    image: Dict
) -> None:
    """Test successful get image returns 200"""
    image_id = image["id"]
    out = client.get(f'/images/{image_id}')
    assert out.status_code == status.HTTP_200_OK
    data = out.json()
    assert data['id'] == image['id']
    assert data['name'] == image['name']
    assert data['size'] == image['size']
    assert data['path'] == image['path']
    assert data['status'] == image['status']
    assert data['information'] == image['information']
    assert data['description'] == image['description']
    assert data['storage_id'] == image['storage_id']
    assert data['user_id'] == image['user_id']


@pytest.mark.parametrize('stor', [True, False])
def test_get_images_success(
    client: TestClient,
    storage: Dict,
    image: Dict,
    *,
    stor: bool
) -> None:
    """Test successful get_images returns 200"""
    storage_id = storage["id"]
    image_id = image['id']
    if stor:
        out = client.get(f'/images/?storage_id={storage_id}')
    else:
        out = client.get('/images/')
    assert out.status_code == status.HTTP_200_OK
    data = out.json()
    assert 'items' in data
    items = data.get('items', {})
    assert any(v.get('id', '') == image_id for v in items)


def test_get_image_unauthorized(
    unauthorized_client: TestClient,
    image: Dict
) -> None:
    """Test unauthorized request returns 401."""
    image_id = image.get('id', '')
    out = unauthorized_client.get(f'/images/{image_id}')
    assert out.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize('stor', [True, False])
def test_get_images_unauthorized(
    unauthorized_client: TestClient,
    storage: Dict,
    *,
    stor: bool
) -> None:
    """Test unauthorized request returns 401."""
    storage_id = storage["id"]
    if stor:
        out = unauthorized_client.get(f'/images/?storage_id={storage_id}')
    else:
        out = unauthorized_client.get('/images/')
    assert out.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_image_invalid_uuid(
    client: TestClient,
) -> None:
    """Test getting image with imvalid uuid returns 500"""
    image_id = str(uuid.uuid4())
    out = client.get(f'/images/{image_id}')
    assert out.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_images_invalid_storage_id(
    client: TestClient,
) -> None:
    """Test get images with nonexcistent storage returns 500."""
    storage_id = str(uuid.uuid4())
    out = client.get(f'/images/?storage_id={storage_id}')
    assert out.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_image_wrong_image_id(
    client: TestClient,
) -> None:
    """Test get image with image_id not uuid returns 422."""
    image_id = "image"
    out = client.get(f'/images/{image_id}')
    assert out.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_images_wrong_storage_id(
    client: TestClient,
) -> None:
    """Test get image with storage_id not uuid returns 422."""
    storage_id = "storage"
    out = client.get(f'/images/?storage_id={storage_id}')
    assert out.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
