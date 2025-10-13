"""Integration tests for port group operations of virtual networks.

Covers:
- Add port group
- Delete port group
- Add tag to trunk port group
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.virtual_network.entrypoints.schemas import PortGroup


def test_add_port_group(client: TestClient, virtual_network: Dict) -> None:
    """Test successful adding of a port group."""
    port_group = PortGroup(
        port_group_name='new_pg', is_trunk='yes', tags=['200']
    ).model_dump(mode='json')

    response = client.post(
        f'/virtual_networks/{virtual_network["id"]}/add_port_group',
        json=port_group
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert any(pg['port_group_name'] == 'new_pg' for pg in data['port_groups'])


def test_delete_port_group(client: TestClient, virtual_network: Dict) -> None:
    """Tests successful deleting of the port group."""
    pg_payload = PortGroup(
        port_group_name='to_delete', is_trunk='yes', tags=['201']
    ).model_dump(mode='json')
    client.post(
        f'/virtual_networks/{virtual_network["id"]}/add_port_group',
        json=pg_payload
    )

    response = client.delete(
        f'/virtual_networks/{virtual_network["id"]}/delete_port_group',
        params={'port_group_name': 'to_delete'},
    )
    assert response.status_code == status.HTTP_200_OK


def test_add_tag_to_trunk_port_group(
    client: TestClient, virtual_network: Dict
) -> None:
    """Tests successful adding tag to trunk port."""
    pg_payload = PortGroup(
        port_group_name='trunk_pg2', is_trunk='yes', tags=['100']
    ).model_dump(mode='json')
    client.post(
        f'/virtual_networks/{virtual_network["id"]}/add_port_group',
        json=pg_payload
    )

    response = client.post(
        f'/virtual_networks/{virtual_network["id"]}/trunk_pg2/300/add_tag_id'
    )
    assert response.status_code == status.HTTP_200_OK
