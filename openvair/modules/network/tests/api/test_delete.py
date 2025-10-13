# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for bridge deletion.

Covers:
- Successful bridge(s) deletion
- Deletion of non-existent bridge, incorrect input data
- Unauthorized access
"""

import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.testing.utils import (
    wait_for_field_not_empty,
    generate_test_entity_name,
    wait_full_deleting_object,
)

LOG = get_logger(__name__)


def _check_connection() -> None:
    """Checks internet connection after bridge creation via ping."""
    for host in ['8.8.8.8', 'google.com', 'ya.ru']:
        exec_res = execute(
            f'ping -c 1 -W 2 {host}',
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        assert exec_res.returncode == 0


def _check_bridge_deleted_in_ovs(bridge_name: str) -> None:
    """Check that bridge is deleted from OVS.

    Args:
        bridge_name: Name of the bridge to check
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
    assert bridge_name not in ovs_bridges


def _check_bridge_deleted_in_netplan(bridge_name: str) -> None:
    """Check that bridge is deleted from Netplan.

    Args:
        bridge_name: Name of the bridge to check
    """
    exec_res = execute(
        f'netplan get network.bridges.{bridge_name}',
        params=ExecuteParams(  # noqa: S604
            run_as_root=True,
            shell=True,
        ),
    )
    assert len(exec_res.stderr) == 0


@pytest.mark.manager('ovs')
def test_delete_bridge_ovs_success(
    check_manager: None,
    client: TestClient,
    bridge: dict,
) -> None:
    """Test successful bridge deletion.

    Asserts:
    - Response is 202 ACCEPTED
    - Response contains list with deleted bridge data
    - Bridge status becomes 'deleting'
    - Bridge is removed from system (OVS)
    """
    delete_data = [bridge['id']]

    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == bridge['id']
    assert data[0]['status'] == 'deleting'

    wait_full_deleting_object(client, '/interfaces/', bridge['id'])
    _check_bridge_deleted_in_ovs(bridge['name'])
    _check_connection()


@pytest.mark.manager('netplan')
def test_delete_bridge_netplan_success(
    check_manager: None,
    client: TestClient,
    bridge: dict,
) -> None:
    """Test successful bridge deletion.

    Asserts:
    - Response is 202 ACCEPTED
    - Response contains list with deleted bridge data
    - Bridge status becomes 'deleting'
    - Bridge is removed from system (Netplan)
    """
    delete_data = [bridge['id']]

    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == bridge['id']
    assert data[0]['status'] == 'deleting'

    wait_full_deleting_object(client, '/interfaces/', bridge['id'])
    _check_bridge_deleted_in_netplan(bridge['name'])
    _check_connection()


@pytest.mark.manager('ovs')
def test_delete_multiple_bridges_ovs_success(
    check_manager: None,
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: dict,
) -> None:
    """Test successful deletion of multiple bridges.

    Asserts:
    - Response is 202 ACCEPTED
    - Response contains list with all deleted bridges data
    """
    bridges_num = 3
    bridges_data = []
    for i in range(bridges_num):
        bridge_data = {
            'name': generate_test_entity_name(f'br{i}'),
            'type': 'bridge',
            'interfaces': [physical_interface],
            'ip': '',
        }
        response = client.post('/interfaces/create/', json=bridge_data)
        assert response.status_code == status.HTTP_201_CREATED
        bridges_data.append(response.json())

    bridge_ids = [br['id'] for br in bridges_data]
    response = client.request('DELETE', '/interfaces/delete/', json=bridge_ids)
    assert response.status_code == status.HTTP_202_ACCEPTED

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == bridges_num
    returned_ids = [item['id'] for item in data]
    for bridge_id in bridge_ids:
        assert bridge_id in returned_ids
        assert any(
            item['status'] == 'deleting'
            for item in data
            if item['id'] == bridge_id
        )

    for bridge_id in bridge_ids:
        wait_full_deleting_object(client, '/interfaces/', bridge_id)
    wait_for_field_not_empty(
        client, f'/interfaces/{physical_interface["id"]}', 'ip'
    )
    bridge_names = [br['name'] for br in bridges_data]
    for bridge_name in bridge_names:
        _check_bridge_deleted_in_ovs(bridge_name)
    _check_connection()


# TODO: Test Netplan when fixed https://github.com/Aerodisk/openvair/issues/260
#       (or other tests will fail due to netplan network errors)
@pytest.mark.manager('netplan')
def test_delete_multiple_bridges_netplan_success(
    check_manager: None,
    client: TestClient,
    cleanup_bridges: None,
    physical_interface: dict,
) -> None:
    """Test successful deletion of multiple bridges."""
    raise AssertionError  # TODO https://github.com/Aerodisk/openvair/issues/260


def test_delete_bridge_nonexistent(
    client: TestClient, cleanup_bridges: None
) -> None:
    """Test deletion of non-existent bridge.

    Asserts:
    - Response is 500 INTERNAL SERVER ERROR
    - Error message indicates bridge not found
    """
    nonexistent_id = str(uuid.uuid4())
    delete_data = [nonexistent_id]
    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_delete_bridge_empty_list(
    client: TestClient, cleanup_bridges: None
) -> None:
    """Test deletion with empty bridge list.

    Asserts:
    - Response is 202 ACCEPTED
    - Response contains empty list
    """
    delete_data: list = []
    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_delete_bridge_invalid_id_format(
    client: TestClient, cleanup_bridges: None
) -> None:
    """Test deletion with invalid ID format.

    Asserts:
    - Response is 422 UNPROCESSABLE ENTITY
    """
    delete_data = ['invalid-id-format']
    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'invalid input syntax for type uuid' in response.text.lower()


def test_delete_bridge_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized bridge deletion.

    Asserts:
    - Response is 401 UNAUTHORIZED
    """
    delete_data = [str(uuid.uuid4())]
    response = unauthorized_client.request(
        'DELETE', '/interfaces/delete/', json=delete_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
