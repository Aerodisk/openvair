"""Integration tests for image deletion API endpoint.

This test suite covers:
- Successful deletion of existing images.
- Handling deletion attempts with invalid UUID formats.
- Behavior when deleting non-existing images.
- Response to unauthorized deletion attempts.
"""

import uuid
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient


def test_delete_image_success(
    client: TestClient,
    image: dict
) -> None:
    """Test successful deleting of the image."""
    image_id = image['id']
    response = client.delete(f'/images/{image_id}')
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f'/images/{image_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    storage_id = image.get('storage_id', ' ')
    storage_type = 'localfs'
    storage_path = f'/opt/aero/openvair/data/mnt/{storage_type}-{storage_id}'
    image_path = Path(storage_path, f'image-{image_id}')
    assert image_path.exists() is False


def test_delete_image_not_uuid(
    client: TestClient
) -> None:
    """Test image not uuid returns 422"""
    image_id = "image"
    response = client.delete(f'/images/{image_id}')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_non_existing_image(
    client: TestClient
) -> None:
    """Test delete an image with non excistant uuid returns 500"""
    image_id = str(uuid.uuid4())
    response = client.delete(f'/images/{image_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete_image_unauthorized(
    image: dict,
    unauthorized_client: TestClient
) -> None:
    """Test successful deleting of the image."""
    image_id = image['id']
    response = unauthorized_client.delete(f'/images/{image_id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
