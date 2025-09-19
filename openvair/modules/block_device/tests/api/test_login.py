"""Integration tests for login endpoint.

Covers:
- Successful login with required and optional fields.
- Validation errors for missing or invalid fields (`inf_type`, `ip`, `port`).
- Unauthorized access to login endpoint.
- Handling of repeated login attempts resulting in server error.
"""

import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import block_device_settings

valid_ip = block_device_settings.ip
valid_port = block_device_settings.port
valid_inf_type = block_device_settings.inf_type


valid_input = {
    "inf_type": valid_inf_type,
    "ip": valid_ip,
    "port": valid_port
}


@pytest.mark.parametrize(
    'input_data', [
        valid_input,
        {k: v for k, v in valid_input.items() if k != "port"}
    ]
)
def test_login_success(
    client_with_logout: TestClient, input_data: dict
) -> None:
    """Test successful login with valid input data, including optional port.

    Asserts:
    - Response status is 200 OK.
    - Returned data contains correct 'inf_type', 'ip', 'port', and status.
    - Returned 'id' is a valid UUID.
    """
    resp = client_with_logout.post("/block-devices/login", json=input_data)
    assert resp.status_code == status.HTTP_200_OK, resp
    response = resp.json()
    assert response['inf_type'] == valid_inf_type
    assert response['ip'] == valid_ip
    assert response['port'] == valid_port
    assert response['status'] == "available"
    try:
        uuid.UUID(response['id'])
    except ValueError:
        assert AssertionError(), f"Invalid UUID: {response['id']}"


@pytest.mark.parametrize(
    'missing_field', ["inf_type", "ip"]
)
def test_login_missing_required_field(
    client_with_logout: TestClient, missing_field: str
) -> None:
    """Test response status is 422 when 'inf_type' or 'ip' is missing."""
    invalid_input = valid_input.copy()
    invalid_input.pop(missing_field)

    response = client_with_logout.post(
        "/block-devices/login",
        json=invalid_input
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized request returns 401."""
    response = unauthorized_client.post('/templates/', json=valid_input)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'invalid_field', [
        ("inf_type", 1),
        ("inf_type", None),
        ("ip", None),
        ("ip", 12),
        ("port", 3260)
    ]
)
def test_login_invalid_required_field_type(
    client_with_logout: TestClient, invalid_field: dict
) -> None:
    """Test response status is 422 for invalid field types."""
    invalid_input = valid_input.copy()
    invalid_input[invalid_field[0]] = invalid_field[1]

    response = client_with_logout.post(
        "/block-devices/login",
        json=invalid_input
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    'invalid_field', [
        ("inf_type", "string"),
        ("ip", "string"),
        ("ip", "127.0.0.1"),
        ("port", "string"),
        ("port", "123123")
    ]
)
def test_login_invalid_required_field(
    client_with_logout: TestClient, invalid_field: dict
) -> None:
    """Test response status is 500 for invalid field values."""
    invalid_input = valid_input.copy()
    invalid_input[invalid_field[0]] = invalid_field[1]

    response = client_with_logout.post(
        "/block-devices/login",
        json=invalid_input
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_double_login(client_with_logout: TestClient) -> None:
    """Second login returns 500 Internal Server Error."""
    response = client_with_logout.post("/block-devices/login", json=valid_input)
    response = client_with_logout.post("/block-devices/login", json=valid_input)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
