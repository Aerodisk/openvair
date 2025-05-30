"""Integration tests for creating templates via API.

Covers:
- Successful creation with both is_backing values.
- Missing required fields.
- Unauthorized access.
- Invalid storage/base_volume_id.
- Edge cases for null and nonexistent base_volume_id.
"""

import uuid
from typing import Dict

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import generate_test_entity_name
from openvair.modules.template.entrypoints.schemas.requests import (
    RequestCreateTemplate,
)


@pytest.mark.parametrize('is_backing', [True, False])
def test_create_template_success(
    client: TestClient,
    storage: Dict,
    volume: Dict,
    *,
    is_backing: bool,
) -> None:
    """Test successful template creation with both is_backing values."""
    request = RequestCreateTemplate(
        base_volume_id=volume['id'],
        name=generate_test_entity_name('template'),
        description='Test template',
        storage_id=storage['id'],
        is_backing=is_backing,
    )
    response = client.post('/templates/', json=request.model_dump(mode='json'))
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()['data']
    assert data['name'] == request.name
    assert data['storage_id'] == str(request.storage_id)
    assert data['is_backing'] is is_backing


@pytest.mark.parametrize(
    'missing_field', ['name', 'storage_id', 'base_volume_id']
)
def test_create_template_missing_required_field(
    client: TestClient,
    storage: Dict,
    volume: Dict,
    missing_field: str,
) -> None:
    """Test that missing required fields result in HTTP 422."""
    request_data: Dict = {
        'base_volume_id': volume['id'],
        'name': generate_test_entity_name('template'),
        'description': 'Test',
        'storage_id': storage['id'],
        'is_backing': True,
    }
    request_data.pop(missing_field)
    response = client.post('/templates/', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_template_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized request returns 401."""
    request_data: Dict = RequestCreateTemplate(
        base_volume_id=uuid.uuid4(),
        name=generate_test_entity_name('template'),
        description='Unauthorized attempt',
        storage_id=uuid.uuid4(),
        is_backing=False,
    ).model_dump(mode='json')

    response = unauthorized_client.post('/templates/', json=request_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_template_with_invalid_storage_id(
    client: TestClient,
    volume: Dict,
) -> None:
    """Test creation with nonexistent storage_id returns 500."""
    request_data: Dict = {
        'base_volume_id': volume['id'],
        'name': generate_test_entity_name('template'),
        'description': 'Invalid storage',
        'storage_id': str(uuid.uuid4()),
        'is_backing': True,
    }
    response = client.post('/templates/', json=request_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_template_missing_base_volume(
    client: TestClient,
    storage: Dict,
) -> None:
    """Test creation without base_volume_id returns 422."""
    request_data: Dict = {
        'name': generate_test_entity_name('template'),
        'description': 'Missing base_volume_id',
        'storage_id': storage['id'],
        'is_backing': True,
    }
    response = client.post('/templates/', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_template_with_null_base_volume_id(
    client: TestClient,
    storage: Dict,
) -> None:
    """Test creation with null base_volume_id returns 422."""
    request_data: Dict = {
        'base_volume_id': None,
        'name': generate_test_entity_name('template'),
        'description': 'Null base_volume_id',
        'storage_id': storage['id'],
        'is_backing': True,
    }
    response = client.post('/templates/', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_template_with_nonexistent_base_volume(
    client: TestClient,
    storage: Dict,
) -> None:
    """Test creation with nonexistent base_volume_id returns 500."""
    request_data: Dict = {
        'base_volume_id': str(uuid.uuid4()),
        'name': generate_test_entity_name('template'),
        'description': 'Nonexistent volume',
        'storage_id': storage['id'],
        'is_backing': True,
    }
    response = client.post('/templates/', json=request_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
