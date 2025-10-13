"""Integration tests for image retrieval API endpoints.

This test suite covers:
- Successful retrieval of individual images and lists of images.
- Retrieval with and without filtering by storage ID.
- Handling unauthorized access attempts.
- Validation of UUID formats in image and storage IDs.
- Behavior when fetching images or storages that do not exist.
"""

import uuid

from fastapi import status
from fastapi.testclient import TestClient


def test_get_image_success(
    client: TestClient,
    image: dict
) -> None:
    """Test successful get image returns 200"""
    image_id = image["id"]
    response = client.get(f'/images/{image_id}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == image['id']
    assert data['name'] == image['name']
    assert data['size'] == image['size']
    assert data['path'] == image['path']
    assert data['status'] == image['status']
    assert data['information'] == image['information']
    assert data['description'] == image['description']
    assert data['storage_id'] == image['storage_id']
    assert data['user_id'] == image['user_id']


def test_get_images_success(
    client: TestClient,
    image: dict,
) -> None:
    """Test successful get_images returns 200"""
    image_id = image['id']
    response = client.get('/images/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'items' in data
    items = data.get('items', {})
    assert any(v.get('id', '') == image_id for v in items)


def test_get_image_unauthorized(
    image: dict,
    unauthorized_client: TestClient
) -> None:
    """Test unauthorized request returns 401."""
    image_id = image.get('id', '')
    response = unauthorized_client.get(f'/images/{image_id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_images_unauthorized(
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized request returns 401."""
    response = unauthorized_client.get('/images/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_image_invalid_image_id(
    client: TestClient,
) -> None:
    """Test getting nonexcistent image returns 500"""
    image_id = str(uuid.uuid4())
    response = client.get(f'/images/{image_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_images_invalid_storage_id(
    client: TestClient,
) -> None:
    """Test get images with nonexcistent storage returns 500."""
    storage_id = str(uuid.uuid4())
    response = client.get(f'/images/?storage_id={storage_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_image_wrong_image_id(
    client: TestClient,
) -> None:
    """Test get image with image_id not uuid returns 422."""
    image_id = "image"
    response = client.get(f'/images/{image_id}')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_images_wrong_storage_id(
    client: TestClient,
) -> None:
    """Test get image with storage_id not uuid returns 422."""
    storage_id = "storage"
    response = client.get(f'/images/?storage_id={storage_id}')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
