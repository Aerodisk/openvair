"""Integration tests for editing templates via API.

Covers:
- Successful updates (name, description, both) with async status check.
- Validation and edge cases (length, missing body, bad UUID).
- Unauthorized access and missing template.
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import wait_for_field_value


def test_edit_template_name_success(client: TestClient, template: Dict) -> None:
    """Test successful update of template name."""
    new_name = 'updated-name'
    response = client.patch(
        f"/templates/{template['id']}", json={'name': new_name}
    )
    assert response.status_code == status.HTTP_200_OK

    wait_for_field_value(
        client, f"/templates/{template['id']}/", 'status', 'available'
    )

    get_response = client.get(f"/templates/{template['id']}/")
    data = get_response.json()['data']
    assert data['name'] == new_name
    assert data['status'] == 'available'


def test_edit_template_description_success(
    client: TestClient, template: Dict
) -> None:
    """Test successful update of template description."""
    new_description = 'Updated description for the template'
    response = client.patch(
        f"/templates/{template['id']}",
        json={'description': new_description},
    )
    assert response.status_code == status.HTTP_200_OK

    wait_for_field_value(
        client, f"/templates/{template['id']}/", 'status', 'available'
    )

    get_response = client.get(f"/templates/{template['id']}/")
    data = get_response.json()['data']
    assert data['description'] == new_description
    assert data['status'] == 'available'


def test_edit_template_both_fields_success(
    client: TestClient, template: Dict
) -> None:
    """Test successful update of both name and description."""
    new_name = 'updated-template'
    new_description = 'Updated description'
    response = client.patch(
        f"/templates/{template['id']}",
        json={'name': new_name, 'description': new_description},
    )
    assert response.status_code == status.HTTP_200_OK

    wait_for_field_value(
        client, f"/templates/{template['id']}/", 'status', 'available'
    )

    get_response = client.get(f"/templates/{template['id']}/")
    data = get_response.json()['data']
    assert data['name'] == new_name
    assert data['description'] == new_description
    assert data['status'] == 'available'


def test_edit_template_invalid_name_too_short(
    client: TestClient, template: Dict
) -> None:
    """Test that empty name is rejected (min_length=1)."""
    response = client.patch(f"/templates/{template['id']}", json={'name': ''})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_template_invalid_name_too_long(
    client: TestClient, template: Dict
) -> None:
    """Test that too long name (>40) is rejected."""
    long_name = 'a' * 41
    response = client.patch(
        f"/templates/{template['id']}", json={'name': long_name}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_template_invalid_description_too_long(
    client: TestClient, template: Dict
) -> None:
    """Test that too long description (>255) is rejected."""
    long_description = 'd' * 256
    response = client.patch(
        f"/templates/{template['id']}",
        json={'description': long_description},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_template_empty_body(client: TestClient, template: Dict) -> None:
    """Test that empty request body is rejected."""
    response = client.patch(f"/templates/{template['id']}", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_template_nonexistent_id(client: TestClient) -> None:
    """Test that editing nonexistent template returns 500."""
    fake_id = str(uuid.uuid4())
    response = client.patch(f'/templates/{fake_id}', json={'name': 'new-name'})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_edit_template_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID returns 422."""
    response = client.patch('/templates/invalid-uuid', json={'name': 'fail'})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_template_unauthorized(
    template: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized edit attempt returns 401."""
    response = unauthorized_client.patch(
        f"/templates/{template['id']}", json={'name': 'new'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
