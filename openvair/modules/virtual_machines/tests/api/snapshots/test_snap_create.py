"""Integration tests for virtual machine snapshots creation.

Covers:
- Successful snapshot creation.
- Validation errors (e.g. missing fields, invalid config).
- Logical errors (e.g. duplicate name, shutdown VM).
- Unauthorized access.
"""

import uuid
from typing import Dict

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.libvirt.vm import get_vm_snapshots
from openvair.libs.testing.utils import (
    wait_for_field_value,
    generate_test_entity_name,
)
from openvair.modules.virtual_machines.tests.conftest import SNAPSHOT_TIMEOUT


def test_create_snapshot_success(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test successful snapshot creation."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    snapshot_data = {
        'name': generate_test_entity_name('snapshot'),
        'description': 'Test successful snapshot creation',
    }

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'id' in data
    assert data['name'] == snapshot_data['name']
    assert data['description'] == snapshot_data['description']
    assert data['vm_id'] == vm_id
    assert data['vm_name'] == vm_name
    assert data['parent'] is None
    assert 'created_at' in data
    assert data['created_at'] != ''

    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{data["id"]}',
        'status',
        'running',
        timeout=SNAPSHOT_TIMEOUT,
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{data["id"]}',
        'is_current',
        expected=True,
        timeout=SNAPSHOT_TIMEOUT,
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'power_state',
        'running',
    )

    created_snapshot = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{data["id"]}'
    ).json()
    assert created_snapshot['status'] == 'running'
    assert created_snapshot['is_current'] is True
    libvirt_snapshots, current_snapshot = get_vm_snapshots(vm_name)
    assert snapshot_data['name'] in libvirt_snapshots
    assert current_snapshot == snapshot_data['name']


def test_create_snapshot_missing_name(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test snapshot creation with missing required name field."""
    vm_id = activated_virtual_machine['id']

    response = client.post(f'/virtual-machines/{vm_id}/snapshots/', json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_snapshot_duplicate_name(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test snapshot creation with duplicate name."""
    vm_id = activated_virtual_machine['id']
    snapshot_data = {
        'name': 'duplicate_snapshot',
        'description': 'First snapshot',
    }

    response1 = client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response1.status_code == status.HTTP_201_CREATED

    response2 = client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'exist' in response2.text.lower()


def test_create_snapshot_shutoff_vm(
    client: TestClient, deactivated_virtual_machine: Dict
) -> None:
    """Test snapshot creation on shut down VM."""
    vm_id = deactivated_virtual_machine['id']
    snapshot_data = {
        'name': generate_test_entity_name('snapshot'),
        'description': 'Test snapshot on stopped VM',
    }

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'power' in response.text.lower()


def test_create_snapshot_nonexistent_vm(client: TestClient) -> None:
    """Test snapshot creation for nonexistent VM."""
    nonexistent_vm_id = str(uuid.uuid4())
    snapshot_data = {
        'name': generate_test_entity_name('snapshot'),
        'description': 'Test snapshot',
    }

    response = client.post(
        f'/virtual-machines/{nonexistent_vm_id}/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


@pytest.mark.parametrize('invalid_name', ['a' * 256, ''])
def test_create_snapshot_invalid_name(
    client: TestClient, activated_virtual_machine: Dict, invalid_name: str
) -> None:
    """Test snapshot creation with invalid name."""
    vm_id = activated_virtual_machine['id']
    snapshot_data = {'name': invalid_name, 'description': 'Test snapshot'}

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_snapshot_no_description(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test snapshot creation without description."""
    vm_id = activated_virtual_machine['id']
    snapshot_data = {'name': generate_test_entity_name('snapshot')}

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_create_snapshot_invalid_vm_uuid(client: TestClient) -> None:
    """Test snapshot creation with invalid VM UUID format."""
    snapshot_data = {
        'name': generate_test_entity_name('snapshot'),
        'description': 'Test snapshot',
    }

    response = client.post(
        '/virtual-machines/invalid-uuid/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_multiple_snapshots_chain(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test creating multiple snapshots in chain with parent relationships."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    snapshots = []
    snapshots_num = 3

    for i in range(snapshots_num):
        snapshot_data = {
            'name': f'chain_snapshot_{i}',
            'description': f'Chain snapshot {i}',
        }

        response = client.post(
            f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        snapshot = response.json()
        snapshots.append(snapshot)
        wait_for_field_value(
            client,
            f'/virtual-machines/{vm_id}/snapshots/{snapshot["id"]}',
            'status',
            'running',
            timeout=SNAPSHOT_TIMEOUT,
        )
        wait_for_field_value(
            client,
            f'/virtual-machines/{vm_id}/snapshots/{snapshot["id"]}',
            'is_current',
            expected=True,
            timeout=SNAPSHOT_TIMEOUT,
        )
        wait_for_field_value(
            client,
            f'/virtual-machines/{vm_id}/',
            'power_state',
            'running',
        )

    libvirt_snapshots, current_snapshot = get_vm_snapshots(vm_name)
    assert current_snapshot == f'chain_snapshot_{snapshots_num-1}'

    for i, snapshot in enumerate(snapshots):
        snapshot_details = client.get(
            f'/virtual-machines/{vm_id}/snapshots/{snapshot["id"]}'
        ).json()

        assert snapshot_details['status'] == 'running'
        assert snapshot_details['is_current'] == (i == snapshots_num - 1)
        assert snapshot_details['name'] == f'chain_snapshot_{i}'
        assert snapshot_details['vm_id'] == vm_id
        assert snapshot_details['vm_name'] == vm_name
        assert (
            snapshot_details['parent'] is None
            if (i == 0)
            else (f'chain_snapshot_{i-1}')
        )
        assert f'chain_snapshot_{i}' in libvirt_snapshots


def test_create_snapshot_unauthorized(
    activated_virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized snapshot creation request."""
    vm_id = activated_virtual_machine['id']
    snapshot_data = {
        'name': generate_test_entity_name('snapshot'),
        'description': 'Test snapshot',
    }

    response = unauthorized_client.post(
        f'/virtual-machines/{vm_id}/snapshots/', json=snapshot_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
