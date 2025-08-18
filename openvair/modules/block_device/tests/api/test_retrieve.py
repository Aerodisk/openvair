"""Integration tests for IQN retrieval and LIP scan endpoints.

Covers:
- Successful retrieval of host IQN with format validation.
- Unauthorized access attempts to IQN endpoint.
- Successful execution of LIP scan on Fibre Channel adapters.
- Unauthorized access attempts to LIP scan endpoint.
"""

import re

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import block_device_settings

valid_ip = block_device_settings.ip
valid_inf_type = block_device_settings.inf_type


def test_ign_success(client: TestClient) -> None:
    """Test successful retrieval of IQN.

    Asserts:
    - Response status is 200 OK.
    - Returned IQN matches expected IQN format.
    """
    resp = client.get("/block-devices/get-iqn")
    assert resp.status_code == status.HTTP_200_OK, resp
    response = resp.json()
    pattern = r'^iqn\.(\d{4})-(\d{2})\.[a-z0-9\-]+(?:\.[a-z0-9\-]+)*(:[^\s]+)?$'
    assert bool(re.match(pattern, response["iqn"])) is True


def test_ign_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized request returns 401."""
    resp = unauthorized_client.get("/block-devices/get-iqn")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_lip_scan_success(client: TestClient) -> None:
    """Test successful LIP scan execution.

    Asserts:
    - Response status is 200 OK.
    - Response text matches expected success message.
    """
    resp = client.get("/block-devices/lip_scan")
    assert resp.status_code == status.HTTP_200_OK, resp
    response = resp.json()
    assert response == (
        "Successful finished to scan on Fibre Channel host adapters."
    )


def test_lip_scan_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized request returns 401."""
    resp = unauthorized_client.get("/block-devices/lip_scan")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_sessions(client_with_login: TestClient) -> None:
    """Test retrieving active sessions and effect of logout.

    Asserts:
    - Initially, sessions contain an item with the expected IP.
    - After logout, sessions no longer contain that IP.
    - Each response returns status 200 OK.
    """
    response = client_with_login.get("/block-devices/sessions")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(v['ip'] == valid_ip for v in data)
    response = client_with_login.post(
        "/block-devices/logout",
        json={"inf_type": valid_inf_type, "ip": valid_ip}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client_with_login.get("/block-devices/sessions")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(v['ip'] != valid_ip for v in data)
