"""Integration tests for image deletion API endpoint.

This test suite covers:
- Successful deletion of existing images.
- Handling deletion attempts with invalid UUID formats.
- Behavior when deleting non-existing images.
- Response to unauthorized deletion attempts.
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def test_delete_image_success(
    client: TestClient,
    image: Dict
) -> None:
    """Test successful delete_image returns 200."""
    image_id = image.get('id', '')
    out = client.delete(f'/images/{image_id}')
    assert out.status_code == status.HTTP_200_OK


def test_delete_image_not_uuid(
    client: TestClient
) -> None:
    """Test image not uuid returns 422"""
    image_id = "image"
    out = client.delete(f'/images/{image_id}')
    assert out.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_non_excisting_image(
    client: TestClient
) -> None:
    """Test delete an image with non excistant uuid returns 500"""
    image_id = str(uuid.uuid4())
    out = client.delete(f'/images/{image_id}')
    assert out.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete_image_unauthorized(
    unauthorized_client: TestClient,
    image: Dict
) -> None:
    """Test unauthorized request returns 405."""
    image_id = image.get('id', '')
    out = unauthorized_client.delete(f'/images/{image_id}')
    assert out.status_code == status.HTTP_401_UNAUTHORIZED
