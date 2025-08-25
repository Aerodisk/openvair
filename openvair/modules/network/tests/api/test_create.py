"""Integration tests for bridge creation.

Covers:
- Successful bridge creation
- Validation errors (missing fields)
- Logical errors (duplicate name, nonexistent interface)
- Unauthorized access
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    wait_for_field_value,
    generate_test_entity_name,
)
from openvair.modules.network.domain.utils.ovs_manager import OVSManager

LOG = get_logger(__name__)


def test_create_bridge_success(
    client: TestClient, physical_interface: Dict
) -> None:
    """Test successful bridge creation.

    Asserts:
    - Response is 201 CREATED
    - Returned fields match request
    - Bridge status became 'available'
    - Bridge is created in OVS
    """
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    required_fields = [
        'id',
        'ip',
        'name',
        'gateway',
        'power_state',
        'mac',
        'inf_type',
        'status',
        'interface_extra_specs',
    ]
    for field in required_fields:
        assert field in data
    assert data['name'] == bridge_data['name']

    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'status', 'available'
    )
    ovs_bridges = OVSManager().get_bridges()
    name_index = ovs_bridges['headings'].index('name')
    ovs_bridges_names = [br[name_index] for br in ovs_bridges['data']]
    assert data['name'] in ovs_bridges_names


def test_create_bridge_missing_name(
    client: TestClient, physical_interface: Dict
) -> None:
    """Test creation failure when 'name' is missing.

    Asserts:
    - HTTP 422 due to validation error
    """
    bridge_data = {
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_bridge_empty_interfaces(client: TestClient) -> None:
    """Test creation failure with empty interfaces list.

    Asserts:
    - HTTP 422 due to validation error
    """
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_bridge_duplicate_name(
    client: TestClient, physical_interface: Dict, bridge: Dict
) -> None:
    """Test failure when creating bridge with duplicate name.

    Asserts:
    - Second request returns HTTP 500
    """
    bridge_data = {
        'name': bridge['name'],
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'interfacealreadyexist' in response.text.lower()


def test_create_bridge_nonexistent_interface(client: TestClient) -> None:
    """Test failure when interface doesn't exist.

    Asserts:
    - HTTP 500 with interface error message
    """
    nonexistent_interface = {
        'id': str(uuid.uuid4()),
        'name': 'nonexistent',
        'mac': '00:11:22:33:44:55',
        'inf_type': 'physical',
        'power_state': 'on',
    }

    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [nonexistent_interface],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'interface' in response.text.lower()


def test_create_bridge_unauthorized(
    physical_interface: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized request returns 401.

    Asserts:
    - HTTP 401 Unauthorized
    """
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response = unauthorized_client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
