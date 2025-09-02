"""Fixtures for managing login and logout states of block devices during tests.

Includes:
- client_with_logout: Ensures the block_device is logged out before and after
    the test.
- client_with_login: Logs in the block_device before a test.
- client_with_login_and_logout: Logs in before and logs out after a test.
"""

import contextlib
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from openvair.libs.testing.config import block_device_settings

valid_ip = block_device_settings.ip
valid_port = block_device_settings.port
valid_inf_type = block_device_settings.inf_type

@pytest.fixture(scope="function")
def client_with_logout(client: TestClient) -> Generator[TestClient, None, None]:
    """Fixture that logs out the client before and after the test function.

    Ensures tests start and end with a logged-out block_device.
    """
    with contextlib.suppress(Exception):
        client.post(
            "/block-devices/logout",
            json={"ip": valid_ip, "inf_type": valid_inf_type}
        )
    yield client
    with contextlib.suppress(Exception):
        client.post(
            "/block-devices/logout",
            json={"ip": valid_ip, "inf_type": valid_inf_type}
        )

login_data = {"ip": valid_ip, "inf_type": valid_inf_type, "port": valid_port}

@pytest.fixture(scope="function")
def client_with_login(client: TestClient) -> Generator[TestClient, None, None]:
    """Fixture that logs in the client before the test function.

    Provides a client session with logged-in block_device.
    """
    with contextlib.suppress(Exception):
        client.post("/block-devices/login", json=login_data)
    yield client
    with contextlib.suppress(Exception):
        client.post(
            "/block-devices/logout",
            json={"ip": valid_ip, "inf_type": valid_inf_type}
        )
