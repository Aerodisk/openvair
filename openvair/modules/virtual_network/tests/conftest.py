from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import (
    create_resource,
    delete_resource,
    generate_test_entity_name,
)
from openvair.modules.virtual_network.entrypoints.schemas import (
    PortGroup,
    VirtualNetwork,
)


@pytest.fixture(scope='function')
def virtual_network(client: TestClient) -> Generator[Dict, None, None]:
    """Create a test virtual network and delete it after each test."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge='br-int',  # test bridge name
        virtual_port_type='openvswitch',
        port_groups=[
            PortGroup(port_group_name='pg', is_trunk='yes', tags=['100'])
        ],
    ).model_dump(mode='json')

    created = create_resource(
        client, '/virtual_networks/create/', payload, 'virtual_network'
    )

    yield created

    delete_resource(client, '/virtual_networks', created['id'], 'virtual_network')
