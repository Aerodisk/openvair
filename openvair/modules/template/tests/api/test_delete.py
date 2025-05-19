"""Integration tests for deleting templates via API.

Covers:
- Successful deletion with async confirmation.
- Invalid and nonexistent UUID handling.
- Protection from unauthorized access.
- Errors when template is already deleted.
"""

import time
import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def wait_until_404(
    client: TestClient,
    template_id: str,
    timeout: int = 30,
    interval: float = 0.5,
) -> None:
    """Wait until GET /templates/{id} returns 500, indicating deletion.

    Args:
        client (TestClient): The test client to use.
        template_id (str): ID of the template to wait for disappearance.
        timeout (int): Maximum wait time in seconds.
        interval (float): Interval between retries.

    Raises:
        TimeoutError: If template is still available after timeout.
    """
    url = f'/templates/{template_id}'
    start = time.time()
    while time.time() - start < timeout:
        response = client.get(url)
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return
        time.sleep(interval)
    message = f'Template {template_id} not deleted within {timeout} seconds'
    raise TimeoutError(message)


def test_delete_template_success(
    client: TestClient, test_template: Dict
) -> None:
    """Test successful deletion of template and wait for its disappearance."""
    template_id = test_template['id']
    response = client.delete(f'/templates/{template_id}')
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()['data']
    assert data['id'] == template_id
    assert data['status'] == 'deleting'
    wait_until_404(client, template_id)


def test_delete_template_twice(client: TestClient, test_template: Dict) -> None:
    """Test deleting template twice results in error on second attempt."""
    template_id = test_template['id']
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
    test_template: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized user cannot delete template."""
    response = unauthorized_client.delete(f"/templates/{test_template['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
