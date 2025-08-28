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


class _FakeLibvirtNetworkAdapter:
    """In-memory fake of LibvirtNetworkAdapter for tests."""

    def __init__(self) -> None:
        # networks keyed by uuid: {id: {name, state, autostart, persistent, xml}}
        if not hasattr(_FakeLibvirtNetworkAdapter, '_store'):
            _FakeLibvirtNetworkAdapter._store = {}
            _FakeLibvirtNetworkAdapter._name_index = {}

    # Query helpers
    def is_network_exist_by_name(self, name: str) -> bool:
        return name in _FakeLibvirtNetworkAdapter._name_index

    def get_network_state(self, net_id: str) -> str:
        return _FakeLibvirtNetworkAdapter._store.get(net_id, {}).get('state', 'inactive')

    def get_network_autostart(self, net_id: str) -> str:
        return _FakeLibvirtNetworkAdapter._store.get(net_id, {}).get('autostart', 'no')

    def get_network_persistent(self, net_id: str) -> str:
        return _FakeLibvirtNetworkAdapter._store.get(net_id, {}).get('persistent', 'yes')

    def get_network_xml_by_uuid(self, net_id: str) -> str:
        return _FakeLibvirtNetworkAdapter._store.get(net_id, {}).get('xml', '<network/>')

    def get_network_xml_by_name(self, name: str) -> str:
        net_id = _FakeLibvirtNetworkAdapter._name_index.get(name)
        if not net_id:
            return '<network/>'
        return self.get_network_xml_by_uuid(net_id)

    # Lifecycle controls
    def define_network(self, xml: str) -> None:
        # very naive extraction of <name>...</name> and <uuid>...</uuid>
        def _extract(tag: str, default: str) -> str:
            start = xml.find(f'<{tag}>')
            end = xml.find(f'</{tag}>')
            if start != -1 and end != -1:
                return xml[start + len(tag) + 2 : end]
            return default

        name = _extract('name', 'unnamed')
        net_id = _extract('uuid', name)
        _FakeLibvirtNetworkAdapter._store[net_id] = {
            'name': name,
            'state': 'inactive',
            'autostart': 'no',
            'persistent': 'yes',
            'xml': xml,
        }
        _FakeLibvirtNetworkAdapter._name_index[name] = net_id

    def enable_network(self, net_id: str) -> None:
        if net_id in _FakeLibvirtNetworkAdapter._store:
            _FakeLibvirtNetworkAdapter._store[net_id]['state'] = 'active'

    def disable_network(self, net_id: str) -> None:
        if net_id in _FakeLibvirtNetworkAdapter._store:
            _FakeLibvirtNetworkAdapter._store[net_id]['state'] = 'inactive'

    def undefine_network(self, net_id: str) -> None:
        entry = _FakeLibvirtNetworkAdapter._store.pop(net_id, None)
        if entry:
            _FakeLibvirtNetworkAdapter._name_index.pop(entry.get('name', ''), None)


@pytest.fixture(autouse=True)
def mock_libvirt_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Autouse fixture to replace LibvirtNetworkAdapter with in-memory fake."""
    monkeypatch.setattr(
        'openvair.libs.libvirt.network.LibvirtNetworkAdapter',
        _FakeLibvirtNetworkAdapter,
    )


@pytest.fixture(scope='function')
def virtual_network(client: TestClient) -> Generator[Dict, None, None]:
    """Create a test virtual network and delete it after each test."""
    payload = VirtualNetwork(
        network_name=generate_test_entity_name('vnet'),
        forward_mode='bridge',
        bridge='br-int',  # test bridge name; not validated by fake
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