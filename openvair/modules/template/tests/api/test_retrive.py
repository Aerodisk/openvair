# noqa: D100
import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


def test_get_templates_success(client: TestClient, test_template: Dict) -> None:
    """Test successful retrieval of templates.

    Asserts:
    - Response is 200 OK.
    - Response contains paginated data.
    - Response data format matches TemplateResponse model.
    """
    response = client.get('/templates/')
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()['data']
    assert 'items' in data
    assert any(v['id'] == test_template['id'] for v in data['items'])


def test_get_templates_empty_response(client: TestClient) -> None:
    """Test retrieval of templates when there are no templates."""
    response = client.get('/templates/')
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'items' in data['data']
    assert len(data['data']['items']) == 0


def test_get_templates_with_pagination(
    client: TestClient,
) -> None:
    """Test that pagination metadata is returned correctly."""
    response = client.get('/templates/?page=1&size=1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()['data']
    assert 'items' in data
    assert 'total' in data
    assert 'page' in data
    assert 'size' in data
    assert data['page'] == 1
    assert data['size'] == 1


def test_get_existing_template_by_id(
    client: TestClient, test_template: dict
) -> None:
    """Test retrieving template by ID returns correct data."""
    template_id = test_template['id']
    response = client.get(f'/templates/{template_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()['data']
    assert data['id'] == template_id
    assert data['name'] == test_template['name']
    assert data['storage_id'] == test_template['storage_id']


def test_get_nonexistent_template_by_id(client: TestClient) -> None:
    """Test requesting nonexistent UUID returns HTTP 500."""
    fake_volume_id = str(uuid.uuid4())
    response = client.get(f'/templates/{fake_volume_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_volume_with_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID format in path returns HTTP 422."""
    response = client.get('/templates/invalid-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
