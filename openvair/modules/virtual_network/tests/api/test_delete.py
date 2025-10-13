"""Integration tests for deleting virtual networks via API.

Covers:
- Successful deletion with minimal valid payload
- Unauthorized access
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient


def test_delete_virtual_network_success(
    client: TestClient,
    virtual_network: Dict
) -> None:
    """Test successful virtual network deletion."""
    response = client.delete(f'/virtual_networks/{virtual_network["id"]}')

    assert response.status_code == status.HTTP_200_OK
    assert response.text == ('"Deleting command was successful send for '
                             f'Virtual network {virtual_network["id"]}"')


def test_delete_virtual_network_wrong_uuid(client: TestClient) -> None:
    """Test server error while deleting non excistant virtual network."""
    response = client.delete(f'/virtual_networks/{uuid.uuid4()}')

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete_virtual_network_unauthorized(
    virtual_network: Dict,
    unauthorized_client: TestClient
) -> None:
    """Test unauthorized client gets 401 error."""
    response = unauthorized_client.delete(
        f'/virtual_networks/{virtual_network["id"]}'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
