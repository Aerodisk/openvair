"""Integration tests for virtual machine snapshots deletion.

Covers:
- Successful snapshot deletion from running and shut off VMs
- Validation errors (e.g. invalid IDs)
- Logical errors (e.g. nonexistent VM/snapshot)
- Unauthorized access
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.libvirt.vm import get_vm_snapshots
from openvair.libs.testing.utils import (
    wait_for_field_value,
    wait_full_deleting_object,
)
from openvair.modules.virtual_machines.service_layer.unit_of_work import (
    VMSqlAlchemyUnitOfWork,
)


def test_delete_snapshot_success(
        client: TestClient, vm_snapshot: Dict, activated_virtual_machine: Dict
) -> None:
    """Test successful snapshot deletion from running VM."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    snapshot_id = vm_snapshot['id']
    snapshot_name = vm_snapshot['name']
    libvirt_snapshots, libvirt_current = get_vm_snapshots(vm_name)
    assert snapshot_name in libvirt_snapshots

    response = client.delete(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == snapshot_id
    assert data['status'] == 'deleting'
    wait_full_deleting_object(
        client,
        f'/virtual-machines/{vm_id}/snapshots/',
        snapshot_id
    )

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/')
    assert response.status_code == status.HTTP_200_OK
    list_data = response.json()
    assert len(list_data['snapshots']) == 0
    final_libvirt_snapshots, final_libvirt_current = get_vm_snapshots(vm_name)
    assert snapshot_name not in final_libvirt_snapshots
    assert final_libvirt_current is None
    with VMSqlAlchemyUnitOfWork() as uow:
        assert not uow.snapshots.get(snapshot_id)


def test_delete_snapshot_shutoff_vm_success(
        client: TestClient,
        vm_snapshot: Dict,
        deactivated_virtual_machine: Dict
) -> None:
    """Test successful snapshot deletion from shut off VM."""
    vm_id = deactivated_virtual_machine['id']
    snapshot_id = vm_snapshot['id']

    response = client.delete(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == snapshot_id
    assert data['status'] == 'deleting'
    wait_full_deleting_object(
        client,
        f'/virtual-machines/{vm_id}/snapshots/',
        snapshot_id
    )

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/')
    assert response.status_code == status.HTTP_200_OK
    list_data = response.json()
    assert len(list_data['snapshots']) == 0
    with VMSqlAlchemyUnitOfWork() as uow:
        assert not uow.snapshots.get(snapshot_id)


def test_delete_snapshot_chain_success(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test snapshot chain recovery when deleting middle snapshot."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    snapshots = []

    for i in range(3):
        snapshot_data = {
            "name": f"chain_snapshot_{i}",
            "description": f"Chain snapshot {i}"
        }
        response = client.post(
            f'/virtual-machines/{vm_id}/snapshots/',
            json=snapshot_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        snapshot = response.json()
        snapshots.append(snapshot)
        wait_for_field_value(
            client,
            f'/virtual-machines/{vm_id}/snapshots/{snapshot["id"]}',
            'status',
            'running',
            timeout=120
        )

    snap1, snap2, snap3 = snapshots # Snapshot chain: snap1 -> snap2 -> snap3
    snap3_details = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snap3["id"]}'
    ).json()
    assert snap3_details['parent'] == snap2["name"]

    # Delete snap2
    response = client.delete(
        f'/virtual-machines/{vm_id}/snapshots/{snap2["id"]}'
    )
    assert response.status_code == status.HTTP_200_OK
    wait_full_deleting_object(
        client,
        f'/virtual-machines/{vm_id}/snapshots/',
        snap2["id"]
    )

    # Now snap3 should have snap1 as parent
    snap3_details_after = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snap3["id"]}'
    ).json()
    assert snap3_details_after['parent'] == snap1["name"]

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/')
    assert response.status_code == status.HTTP_200_OK
    list_data = response.json()
    assert len(list_data['snapshots']) == len(snapshots) - 1
    remaining_snapshot_names = {s['name'] for s in list_data['snapshots']}
    assert snap1["name"] in remaining_snapshot_names
    assert snap3["name"] in remaining_snapshot_names
    assert snap2["name"] not in remaining_snapshot_names
    libvirt_snapshots, current_snapshot = get_vm_snapshots(vm_name)
    assert snap1["name"] in libvirt_snapshots
    assert snap3["name"] in libvirt_snapshots
    assert snap2["name"] not in libvirt_snapshots


def test_delete_snapshot_invalid_vm_uuid(client: TestClient) -> None:
    """Test deletion attempt using invalid VM UUID format."""
    snapshot_id = str(uuid.uuid4())

    response = client.delete(
        f'/virtual-machines/invalid-uuid/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_snapshot_invalid_snapshot_uuid(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test deletion attempt using invalid snapshot UUID format."""
    vm_id = activated_virtual_machine['id']

    response = client.delete(
        f'/virtual-machines/{vm_id}/snapshots/invalid-uuid'
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_snapshot_nonexistent_vm(client: TestClient) -> None:
    """Test deletion attempt for snapshot of nonexistent VM."""
    nonexistent_vm_id = str(uuid.uuid4())
    snapshot_id = str(uuid.uuid4())

    response = client.delete(
        f'/virtual-machines/{nonexistent_vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_delete_snapshot_nonexistent_snapshot(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test deletion attempt for nonexistent snapshot."""
    vm_id = activated_virtual_machine['id']
    nonexistent_snapshot_id = str(uuid.uuid4())

    response = client.delete(
        f'/virtual-machines/{vm_id}/snapshots/{nonexistent_snapshot_id}'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_delete_snapshot_wrong_vm(
        client: TestClient, vm_snapshot: Dict
) -> None:
    """Test deletion attempt with correct snapshot ID but wrong VM ID."""
    wrong_vm_id = str(uuid.uuid4())
    snapshot_id = vm_snapshot['id']

    response = client.delete(
        f'/virtual-machines/{wrong_vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_delete_snapshot_unauthorized(
        vm_snapshot: Dict,
        activated_virtual_machine: Dict,
        unauthorized_client: TestClient,
) -> None:
    """Test unauthorized snapshot deletion attempt."""
    vm_id = activated_virtual_machine['id']
    snapshot_id = vm_snapshot['id']

    response = unauthorized_client.delete(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
