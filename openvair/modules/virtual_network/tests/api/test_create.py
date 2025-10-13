"""Integration tests for creating virtual networks via API.

Covers:
- Successful creation with minimal valid payload
- Validation: empty port_groups
- Unauthorized access
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import generate_test_entity_name
from openvair.modules.virtual_network.entrypoints.schemas import (
    PortGroup,
    VirtualNetwork,
)


def test_create_virtual_network_success(
    client: TestClient,
    bridge: Dict
) -> None:
    """Test successful virtual network creation."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge=bridge['name'],
        virtual_port_type='openvswitch',
        port_groups=[
            PortGroup(port_group_name='trunk_pg', is_trunk='yes', tags=['100'])
        ],
    ).model_dump(mode='json')

    response = client.post('/virtual_networks/create/', json=payload)
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['network_name'] == payload['network_name']
    assert data['forward_mode'] == payload['forward_mode']
    assert data['bridge'] == payload['bridge']
    assert data['virtual_port_type'] == payload['virtual_port_type']
    assert data['port_groups'][0]['port_group_name'] == 'trunk_pg'


def test_create_virtual_network_missing_port_groups(
    client: TestClient,
    bridge: Dict
) -> None:
    """port_groups must not be empty."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge=bridge['name'],
        virtual_port_type='openvswitch',
        port_groups=[
            PortGroup(port_group_name='trunk_pg', is_trunk='yes', tags=['100'])
        ],
    ).model_dump(mode='json')
    payload.pop('port_groups')

    response = client.post('/virtual_networks/create/', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_virtual_network_unauthorized(
    bridge: Dict,
    unauthorized_client: TestClient
) -> None:
    """Test successful virtual network creation."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge=str(bridge['name']),
        virtual_port_type='openvswitch',
        port_groups=[
            PortGroup(port_group_name='trunk_pg', is_trunk='yes', tags=['100'])
        ],
    ).model_dump(mode='json')

    response = unauthorized_client.post(
        '/virtual_networks/create/',
        json=payload
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
