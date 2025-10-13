"""Integration tests for deleting templates via API.

Covers:
- Successful deletion with async confirmation.
- Invalid and nonexistent UUID handling.
- Protection from unauthorized access.
- Errors when template is already deleted.
"""

import uuid

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import wait_until_404


def test_delete_template_success(client: TestClient, template: dict) -> None:
    """Test successful deletion of template and wait for its disappearance."""
    template_id = template['id']
    response = client.delete(f'/templates/{template_id}')
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()['data']
    assert data['id'] == template_id
    assert data['status'] == 'deleting'
    wait_until_404(client, template_id)


def test_delete_template_twice(client: TestClient, template: dict) -> None:
    """Test deleting template twice results in error on second attempt."""
    template_id = template['id']
    response = client.delete(f'/templates/{template_id}')
    assert response.status_code == status.HTTP_202_ACCEPTED
    wait_until_404(client, template_id)

    second_response = client.delete(f'/templates/{template_id}')
    assert second_response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete_template_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID format returns 422."""
    response = client.delete('/templates/not-a-uuid')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_template_nonexistent_id(client: TestClient) -> None:
    """Test deleting nonexistent UUID returns 500."""
    random_id = str(uuid.uuid4())
    response = client.delete(f'/templates/{random_id}')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete_template_unauthorized(
    template: dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized user cannot delete template."""
    response = unauthorized_client.delete(f"/templates/{template['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
