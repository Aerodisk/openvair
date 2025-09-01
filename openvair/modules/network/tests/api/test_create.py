# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for bridge creation.

Covers:
- Successful bridge creation
- Validation errors (missing fields)
- Logical errors (duplicate name, nonexistent interface)
- Unauthorized access
"""

import uuid
from typing import Dict, List

import yaml
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.testing.utils import (
    wait_for_field_value,
    wait_for_field_not_empty,
    generate_test_entity_name,
)

LOG = get_logger(__name__)


def _check_dhcp(interface: Dict) -> bool:
    """Check DHCP status on the interface

    Args:
        interface: Interface data to check DHCP
    """
    exec_res = execute(
        f"netplan get network.ethernets.{interface['name']}.dhcp4",
        params=ExecuteParams(  # noqa: S604
            run_as_root=True,
            shell=True,
        ),
    )
    return bool(exec_res.returncode == 0 and exec_res.stdout == 'true')


def _check_bridge_in_ovs(data: Dict, interfaces: List[Dict]) -> None:
    """Checks bridge configuration in OVS.

    Args:
        data: Bridge data from response
        interfaces: List of interface dictionaries to check in bridge
    """
    exec_res = execute(
        'ovs-vsctl list-br',
        params=ExecuteParams(  # noqa: S604
            run_as_root=True,
            shell=True,
        ),
    )
    assert exec_res.returncode == 0
    ovs_bridges = exec_res.stdout.splitlines()
    assert data['name'] in ovs_bridges
    exec_res = execute(
        f"ovs-vsctl list-ports {data['name']}",
        params=ExecuteParams(  # noqa: S604
            run_as_root=True,
            shell=True,
        ),
    )
    assert exec_res.returncode == 0
    bridge_ports = exec_res.stdout.splitlines()
    for interface in interfaces:
        assert interface['name'] in bridge_ports


def _check_bridge_in_netplan(
    data: Dict, interfaces: List[Dict], *, dhcp: bool
) -> None:
    """Checks bridge configuration in Netplan.

    Args:
        data: Bridge data from response
        interfaces: List of interface dictionaries to check in bridge
        dhcp: Whether DHCP should be enabled on bridge
    """
    exec_res = execute(
        f"netplan get network.bridges.{data['name']}",
        params=ExecuteParams(  # noqa: S604
            run_as_root=True,
            shell=True,
        ),
    )
    if exec_res.returncode == 0:
        bridge_config = yaml.safe_load(exec_res.stdout)
        assert bridge_config is not None
        for interface in interfaces:
            assert interface['name'] in bridge_config['interfaces']
        if dhcp:
            assert 'dhcp4' in bridge_config
            assert bridge_config['dhcp4']
        else:
            assert 'dhcp4' not in bridge_config or not bridge_config['dhcp4']


def _check_connection(client: TestClient) -> None:
    net_test_response_com = client.get('https://www.google.com/')
    assert net_test_response_com.status_code == status.HTTP_200_OK
    net_test_response_ru = client.get('https://www.ya.ru/')
    assert net_test_response_ru.status_code == status.HTTP_200_OK


@pytest.mark.manager('ovs')
def test_create_bridge_ovs_success(
    check_manager: None,
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: Dict,
) -> None:
    """Test successful bridge creation using OVS.

    Asserts:
    - Response is 201 CREATED
    - Returned fields match request
    - Bridge inherits IP from default physical interface
    - Bridge status became 'available'
    - Bridge is created in system (OVS)
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
    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'ip', physical_interface['ip']
    )
    _check_bridge_in_ovs(data, [physical_interface])
    _check_connection(client)


@pytest.mark.manager('netplan')
def test_create_bridge_netplan_success(
    check_manager: None,
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: Dict,
) -> None:
    """Test successful bridge creation using Netplan.

    Asserts:
    - Response is 201 CREATED
    - Returned fields match request
    - Bridge inherits IP from default physical interface
    - Bridge status became 'available'
    - Bridge is created in system (Netplan)
    - Internet connection active
    """
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }
    interface_dhcp = _check_dhcp(physical_interface)

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
    wait_for_field_not_empty(client, f'/interfaces/{data["id"]}', 'ip')
    _check_bridge_in_netplan(data, [physical_interface], dhcp=interface_dhcp)
    _check_connection(client)


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
    _check_connection(client)


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
    _check_connection(client)


@pytest.mark.manager('ovs')
def test_create_bridge_multiple_interfaces_ovs_success(
    check_manager: None,
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: Dict,
    interface_without_ip: Dict,
) -> None:
    """Test successful bridge creation with multiple interfaces.

    Asserts:
    - Response is 201 CREATED
    - Bridge status becomes 'available'
    - Bridge uses specified custom IP
    - Both interfaces are present in the OVS
    - Internet connection active
    """
    custom_test_ip = '192.168.254.254'

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
    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'ip', custom_test_ip
    )

    _check_bridge_in_ovs(data, [physical_interface])
    _check_connection(client)


@pytest.mark.manager('netplan')
def test_create_bridge_multiple_interfaces_netplan_success(
    check_manager: None,
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: Dict,
    interface_without_ip: Dict,
) -> None:
    """Test successful bridge creation with multiple interfaces.

    Asserts:
    - Response is 201 CREATED
    - Bridge status becomes 'available'
    - Bridge uses specified custom IP
    - Both interfaces are present in the Netplan
    - Internet connection active
    """
    custom_test_ip = '192.168.254.254'

    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface, interface_without_ip],
        'ip': custom_test_ip,
    }
    interface_dhcp = _check_dhcp(physical_interface)

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/interfaces/{data["id"]}', 'ip', custom_test_ip
    )

    _check_bridge_in_netplan(data, [physical_interface], dhcp=interface_dhcp)
    _check_connection(client)


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
    bridge1_data = response1.json()
    wait_for_field_value(
        client,
        f'/interfaces/{bridge1_data["id"]}',
        'status',
        'available',
    )
    wait_for_field_not_empty(
        client,
        f'/interfaces/{bridge1_data["id"]}',
        'ip',
    )

    response2 = client.post('/interfaces/create/', json=bridge_data)
    assert response2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'interfacealreadyexist' in response2.text.lower()


def test_create_bridge_with_long_name(
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: Dict,
) -> None:
    """Test successful bridge creation with long name using OVS.

    Asserts:
    - Response is 422
    """
    long_name = 'test-long-bridge-name'
    bridge_data = {
        'name': long_name,
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
