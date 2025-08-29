# ruff: noqa: ARG001 because of fixtures using
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
    wait_for_field_not_empty,
    generate_test_entity_name,
)
from openvair.modules.network.config import NETWORK_CONFIG_MANAGER
from openvair.modules.network.domain.utils.ovs_manager import OVSManager
from openvair.modules.network.domain.utils.netplan_manager import NetplanManager

LOG = get_logger(__name__)


def test_create_bridge_success(
    client: TestClient, cleanup_bridges: None, physical_interface: Dict
) -> None:
    """Test successful bridge creation.

    Asserts:
    - Response is 201 CREATED
    - Returned fields match request
    - Bridge inherits IP from default physical interface
    - Bridge status became 'available'
    - Bridge is created in system (OVS/Netplan)
    - Internet connection active
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
    if NETWORK_CONFIG_MANAGER == 'ovs':
        if physical_interface['ip']:
            wait_for_field_value(
                client,
                f'/interfaces/{data["id"]}',
                'ip',
                physical_interface['ip']
            )
        ovs_bridges = OVSManager().get_bridges()
        name_index = ovs_bridges['headings'].index('name')
        ovs_bridges_names = [br[name_index] for br in ovs_bridges['data']]
        assert data['name'] in ovs_bridges_names
    else:
        if physical_interface['ip']:
            wait_for_field_not_empty(
                client,
                f'/interfaces/{data["id"]}',
                'ip'
            )
        netplan_manager = NetplanManager()
        bridge_file = netplan_manager.get_path_yaml(data['name'])
        bridge_config = netplan_manager.get_bridge_data_from_yaml(
            data['name'], bridge_file
        )
        assert 'interfaces' in bridge_config
        interface_names = bridge_config['interfaces']
        assert physical_interface['name'] in interface_names

    net_test_response_com = client.get('https://www.google.com/')
    assert net_test_response_com.status_code == status.HTTP_200_OK
    net_test_response_ru = client.get('https://www.ya.ru/')
    assert net_test_response_ru.status_code == status.HTTP_200_OK


def test_create_bridge_custom_ip_success(
    client: TestClient, cleanup_bridges: None, interface_without_ip: Dict
) -> None:
    """Test successful bridge creation with custom IP on interface without ip.

    Asserts:
    - Response is 201 CREATED
    - Bridge uses custom IP instead of inheriting
    - Bridge status became 'available'
    - Internet connection active
    """
    custom_test_ip = '192.168.100.1'

    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [interface_without_ip],
        'ip': custom_test_ip,
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'ip', custom_test_ip
    )
    net_test_response_com = client.get('https://www.google.com/')
    assert net_test_response_com.status_code == status.HTTP_200_OK
    net_test_response_ru = client.get('https://www.ya.ru/')
    assert net_test_response_ru.status_code == status.HTTP_200_OK


def test_create_bridge_missing_name(
    client: TestClient, cleanup_bridges: None, physical_interface: Dict
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


def test_create_bridge_empty_interfaces_success(
    client: TestClient, cleanup_bridges: None
) -> None:
    """Test creation success with empty interfaces list.

    Asserts:
    - HTTP 201 CREATED
    - Status 'available'
    - Internet connection active
    """
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'status', 'available'
    )
    net_test_response_com = client.get('https://www.google.com/')
    assert net_test_response_com.status_code == status.HTTP_200_OK
    net_test_response_ru = client.get('https://www.ya.ru/')
    assert net_test_response_ru.status_code == status.HTTP_200_OK


def test_create_bridge_with_multiple_interfaces(
        client: TestClient,
        cleanup_bridges: None,
        physical_interface: Dict,
        interface_without_ip: Dict
) -> None:
    """Test successful bridge creation with multiple interfaces.

    Asserts:
    - Response is 201 CREATED
    - Bridge status becomes 'available'
    - Bridge uses specified custom IP
    - Both interfaces are present in the system configuration
    - Internet connection active
    """
    custom_test_ip = '192.168.200.1'

    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface, interface_without_ip],
        'ip': custom_test_ip,
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'status', 'available'
    )
    wait_for_field_not_empty(
        client, f'/interfaces/{data["id"]}', 'ip'
    )
    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'ip', custom_test_ip
    )

    if NETWORK_CONFIG_MANAGER == 'ovs':
        ovs_manager = OVSManager()
        ovs_bridges = ovs_manager.get_bridges()
        name_index = ovs_bridges['headings'].index('name')
        ovs_bridges_names = [br[name_index] for br in ovs_bridges['data']]
        assert data['name'] in ovs_bridges_names
        bridge_ports = ovs_manager.get_ports_in_bridge(data['name'])
        assert physical_interface['name'] in bridge_ports
        assert interface_without_ip['name'] in bridge_ports
    else:
        netplan_manager = NetplanManager()
        bridge_file = netplan_manager.get_path_yaml(data['name'])
        bridge_config = netplan_manager.get_bridge_data_from_yaml(
            data['name'], bridge_file
        )
        assert 'interfaces' in bridge_config
        interface_names = bridge_config['interfaces']
        assert physical_interface['name'] in interface_names
        assert interface_without_ip['name'] in interface_names
        if custom_test_ip:
            assert 'addresses' in bridge_config
            addresses = bridge_config['addresses']
            assert any(custom_test_ip in addr for addr in addresses)

    net_test_response_com = client.get('https://www.google.com/')
    assert net_test_response_com.status_code == status.HTTP_200_OK
    net_test_response_ru = client.get('https://www.ya.ru/')
    assert net_test_response_ru.status_code == status.HTTP_200_OK


def test_create_bridge_duplicate_name(
    client: TestClient, cleanup_bridges: None, physical_interface: Dict
) -> None:
    """Test failure when creating bridge with duplicate name.

    Asserts:
    - Second request returns HTTP 500
    """
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response1 = client.post('/interfaces/create/', json=bridge_data)
    assert response1.status_code == status.HTTP_201_CREATED

    response2 = client.post('/interfaces/create/', json=bridge_data)
    assert response2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'interfacealreadyexist' in response2.text.lower()


def test_create_bridge_nonexistent_interface(
    client: TestClient, cleanup_bridges: None
) -> None:
    """Test failure when interface doesn't exist.

    Asserts:
    - Interface status 'error'
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
    data = response.json()
    assert response.status_code in (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_201_CREATED,
    )
    if response.status_code == status.HTTP_201_CREATED:
        wait_for_field_value(
            client, f'/interfaces/{data["id"]}', 'status', 'error'
        )


def test_create_bridge_unauthorized(
    cleanup_bridges: None,
    physical_interface: Dict,
    unauthorized_client: TestClient,
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
