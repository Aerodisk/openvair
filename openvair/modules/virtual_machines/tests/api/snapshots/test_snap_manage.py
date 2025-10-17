"""Integration tests for virtual machine snapshots revert.

Covers:
- Successful snapshot revert on running VM.
- Validation errors (e.g. invalid IDs).
- Logical errors (e.g. nonexistent VM/snapshot, shutoff VM, invalid status).
- Unauthorized access.
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.libvirt.vm import get_vm_snapshots
from openvair.libs.testing.utils import wait_for_field_value
from openvair.modules.virtual_machines.tests.conftest import SNAPSHOT_TIMEOUT


def test_revert_snapshot_success(
    client: TestClient, vm_snapshot: Dict, activated_virtual_machine: Dict
) -> None:
    """Test successful snapshot revert on running VM."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    snapshot_id = vm_snapshot['id']
    snapshot_name = vm_snapshot['name']
    assert vm_snapshot['is_current'] is True

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == snapshot_id
    assert data['status'] == 'reverting'

    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}',
        'status',
        'running',
        timeout=SNAPSHOT_TIMEOUT,
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'power_state',
        'running',
    )

    final_snapshot = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}'
    ).json()
    assert final_snapshot['status'] == 'running'
    assert final_snapshot['is_current'] is True
    libvirt_snapshots_info = get_vm_snapshots(vm_name)
    libvirt_snapshots = libvirt_snapshots_info['snapshots']
    libvirt_current_snapshot = libvirt_snapshots_info['current_snapshot']
    assert final_snapshot['name'] in libvirt_snapshots
    assert libvirt_current_snapshot == snapshot_name


def test_revert_snapshot_chain_success(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test reverting to non-current snapshot in a chain."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    snapshots = []

    for i in range(3):
        snapshot_data = {
            'name': f'chain_snapshot_{i}',
            'description': f'Revert chain snapshot {i}',
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

    snap1, snap2, snap3 = snapshots
    snap3_details = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snap3["id"]}'
    ).json()
    assert snap3_details['is_current'] is True

    # Revert to snap1 (non-current)
    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/{snap1["id"]}/revert'
    )
    assert response.status_code == status.HTTP_200_OK
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{snap1["id"]}',
        'status',
        'running',
        timeout=SNAPSHOT_TIMEOUT,
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'power_state',
        'running',
    )

    # Verify snap1 is now current
    snap1_after = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snap1["id"]}'
    ).json()
    assert snap1_after['is_current'] is True
    libvirt_snapshots_info = get_vm_snapshots(vm_name)
    libvirt_current_snapshot = libvirt_snapshots_info['current_snapshot']
    assert libvirt_current_snapshot == snap1['name']


def test_revert_snapshot_shutoff_vm(
    client: TestClient, vm_snapshot: Dict, deactivated_virtual_machine: Dict
) -> None:
    """Test revert failure on shut off VM."""
    vm_id = deactivated_virtual_machine['id']
    snapshot_id = vm_snapshot['id']

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'power' in response.text.lower()


def test_revert_snapshot_nonexistent_vm(client: TestClient) -> None:
    """Test revert attempt for snapshot of nonexistent VM."""
    nonexistent_vm_id = str(uuid.uuid4())
    snapshot_id = str(uuid.uuid4())

    response = client.post(
        f'/virtual-machines/{nonexistent_vm_id}/snapshots/{snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_revert_snapshot_nonexistent_snapshot(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test revert attempt for nonexistent snapshot."""
    vm_id = activated_virtual_machine['id']
    nonexistent_snapshot_id = str(uuid.uuid4())

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/{nonexistent_snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_revert_snapshot_invalid_vm_uuid(client: TestClient) -> None:
    """Test revert attempt using invalid VM UUID format."""
    snapshot_id = str(uuid.uuid4())

    response = client.post(
        f'/virtual-machines/invalid-uuid/snapshots/{snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_revert_snapshot_invalid_snapshot_uuid(
    client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test revert attempt using invalid snapshot UUID format."""
    vm_id = activated_virtual_machine['id']

    response = client.post(
        f'/virtual-machines/{vm_id}/snapshots/invalid-uuid/revert'
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_revert_snapshot_wrong_vm(
    client: TestClient, vm_snapshot: Dict
) -> None:
    """Test revert attempt with correct snapshot ID but wrong VM ID."""
    wrong_vm_id = str(uuid.uuid4())
    snapshot_id = vm_snapshot['id']

    response = client.post(
        f'/virtual-machines/{wrong_vm_id}/snapshots/{snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_revert_snapshot_unauthorized(
    vm_snapshot: Dict,
    activated_virtual_machine: Dict,
    unauthorized_client: TestClient,
) -> None:
    """Test unauthorized snapshot revert attempt."""
    vm_id = activated_virtual_machine['id']
    snapshot_id = vm_snapshot['id']

    response = unauthorized_client.post(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}/revert'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
