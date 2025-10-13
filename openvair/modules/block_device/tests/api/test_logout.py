"""Integration tests for logout endpoint.

Covers:
- Successful logout with valid input data.
- Validation errors for missing or invalid required fields (`inf_type`, `ip`).
- Unauthorized access to logout endpoint.
- Handling of multiple consecutive logout attempts causing errors.
"""


import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import block_device_settings

valid_ip = block_device_settings.ip
valid_inf_type = block_device_settings.inf_type

valid_request = {
    'inf_type': valid_inf_type,
    'ip': valid_ip,
}


def test_logout_success(client_with_login: TestClient) -> None:
    """Test successful logout with valid data.

    Asserts:
    - Response status is 200 OK.
    - Response contains correct 'inf_type' and 'ip' matching the request.
    """
    resp = client_with_login.post('/block-devices/logout', json=valid_request)
    assert resp.status_code == status.HTTP_200_OK, resp
    response = resp.json()
    assert response['inf_type'] == valid_inf_type
    assert response['ip'] == valid_ip


@pytest.mark.parametrize('missing_field', ['inf_type', 'ip'])
def test_logout_missing_required_field(
    client_with_login: TestClient, missing_field: str
) -> None:
    """Test response status is 422 when 'inf_type' or 'ip' is missing."""
    invalid_request = valid_request.copy()
    invalid_request.pop(missing_field)

    response = client_with_login.post(
        '/block-devices/logout', json=invalid_request
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_logout_unauthorized(unauthorized_client: TestClient) -> None:
    """Test response status is 401 Unauthorized when not logged in."""
    response = unauthorized_client.post('/templates/', json=valid_request)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'invalid_field',
    [
        ('inf_type', 1),
        ('inf_type', None),
        ('ip', None),
        ('ip', 12),
    ],
)
def test_logout_invalid_required_field_type(
    client_with_login: TestClient, invalid_field: dict
) -> None:
    """Test response status is 422 when invalid 'inf_type' or 'ip' types."""
    invalid_request = valid_request.copy()
    invalid_request[invalid_field[0]] = invalid_field[1]

    response = client_with_login.post(
        '/block-devices/logout', json=invalid_request
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    'invalid_field',
    [
        # ("inf_type", "string"),
        ('ip', 'string'),
        ('ip', '127.0.0.1'),
    ],
)
def test_logout_invalid_required_field(
    client_with_login: TestClient, invalid_field: dict
) -> None:
    """Test response status is 500 when invalid 'inf_type' or 'ip' values."""
    invalid_request = valid_request.copy()
    invalid_request[invalid_field[0]] = invalid_field[1]

    response = client_with_login.post(
        '/block-devices/logout', json=invalid_request
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_double_logout(client_with_login: TestClient) -> None:
    """Test second logout returns 500 indicating no active session."""
    response = client_with_login.post(
        '/block-devices/logout', json=valid_request
    )
    assert response.status_code == status.HTTP_200_OK
    response = client_with_login.post(
        '/block-devices/logout', json=valid_request
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
