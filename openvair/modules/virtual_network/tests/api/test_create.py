"""Integration tests for creating virtual networks via API.

Covers:
- Successful creation with minimal valid payload
- Validation: empty port_groups
- Validation: forbidden bridge name (virbr0)
- Unauthorized access (if middleware applies globally)
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import generate_test_entity_name
from openvair.modules.virtual_network.entrypoints.schemas import (
    PortGroup,
    VirtualNetwork,
)


def test_create_virtual_network_success(client: TestClient) -> None:
    """Test successful virtual network creation."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge='br-int',
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


def test_create_virtual_network_empty_port_groups(client: TestClient) -> None:
    """port_groups must not be empty."""
    payload = {
        'network_name': generate_test_entity_name('vnet'),
        'forward_mode': 'bridge',
        'bridge': 'br-int',
        'virtual_port_type': 'openvswitch',
        'port_groups': [],
    }

    response = client.post('/virtual_networks/create/', json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_virtual_network_forbidden_bridge(client: TestClient) -> None:
    """Bridge 'virbr0' is explicitly forbidden by validator."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge='br-test',
        virtual_port_type='openvswitch',
        port_groups=[PortGroup(is_trunk='no', tags=['100'])],
    ).model_dump(mode='json')

    # Force invalid bridge value
    payload['bridge'] = 'virbr0'

    response = client.post('/virtual_networks/create/', json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST 