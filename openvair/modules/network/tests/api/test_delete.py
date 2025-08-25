# ruff: noqa: ARG001 because of fixtures using
"""Integration tests for bridge deletion.

Covers:
- Successful bridge(s) deletion
- Deletion of non-existent bridge, incorrect input data
- Unauthorized access
"""

import uuid
from typing import Dict, List

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    wait_full_deleting,
    generate_test_entity_name,
)
from openvair.modules.network.domain.utils.ovs_manager import OVSManager

LOG = get_logger(__name__)


def test_delete_bridge_success(
    client: TestClient,
    bridge: Dict,
) -> None:
    """Test successful bridge deletion.

    Asserts:
    - Response is 202 ACCEPTED
    - Response contains list with deleted bridge data
    - Bridge status becomes 'deleting'
    - Bridge is eventually removed from OVS
    """
    delete_data = [bridge['id']]

    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

    data = response.json()
    assert isinstance(data, List)
    assert len(data) == 1
    assert data[0]['id'] == bridge['id']
    assert data[0]['status'] == 'deleting'

    wait_full_deleting(client, '/interfaces/', bridge['id'])

    ovs_bridges = OVSManager().get_bridges()
    name_index = ovs_bridges['headings'].index('name')
    ovs_bridges_names = [br[name_index] for br in ovs_bridges['data']]
    assert bridge['name'] not in ovs_bridges_names


def test_delete_multiple_bridges_success(
    client: TestClient, cleanup_bridges: None, physical_interface: Dict
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
    assert isinstance(data, List)
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
        wait_full_deleting(client, '/interfaces/', bridge_id)


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
    delete_data: List = []
    response = client.request('DELETE', '/interfaces/delete/', json=delete_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

    data = response.json()
    assert isinstance(data, List)
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


def test_delete_bridge_unauthorized(
    bridge: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized bridge deletion.

    Asserts:
    - Response is 401 UNAUTHORIZED
    """
    delete_data = [bridge['id']]
    response = unauthorized_client.request(
        'DELETE', '/interfaces/delete/', json=delete_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
