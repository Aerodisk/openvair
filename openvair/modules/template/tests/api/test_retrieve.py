"""Integration tests for retrieving templates via API.

Covers:
- List retrieval with and without data.
- Pagination metadata and parameter validation.
- Retrieving single template by ID.
- Error cases: unauthorized, invalid UUID, nonexistent ID.
"""

import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


def test_get_templates_success(client: TestClient, template: dict) -> None:
    """Test successful retrieval of templates."""
    response = client.get('/templates/')
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()['data']
    assert 'items' in data
    assert any(v['id'] == template['id'] for v in data['items'])


def test_get_templates_empty_response(client: TestClient) -> None:
    """Test retrieval of templates when there are no templates."""
    response = client.get('/templates/')
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()['data']
    assert isinstance(data['items'], list)
    assert len(data['items']) == 0


def test_get_templates_with_pagination(client: TestClient) -> None:
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


@pytest.mark.parametrize('params', ['?page=-1', '?size=0', '?page=abc'])
def test_get_templates_invalid_pagination(
    client: TestClient, params: str
) -> None:
    """Test that invalid pagination parameters return 422."""
    response = client.get(f'/templates/{params}')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_templates_unauthorized(unauthorized_client: TestClient) -> None:
    """Test that access without authentication returns 401."""
    response = unauthorized_client.get('/templates/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_existing_template_by_id(
    client: TestClient, template: dict
) -> None:
    """Test retrieving template by ID returns correct data."""
    template_id = template['id']
    response = client.get(f'/templates/{template_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()['data']
    assert data['id'] == template_id
    assert data['name'] == template['name']
    assert data['storage_id'] == template['storage_id']


def test_get_nonexistent_template_by_id(client: TestClient) -> None:
    """Test requesting nonexistent UUID returns HTTP 500."""
    fake_template_id = str(uuid.uuid4())
    response = client.get(f'/templates/{fake_template_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_template_with_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID format in path returns HTTP 422."""
    response = client.get('/templates/invalid-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
