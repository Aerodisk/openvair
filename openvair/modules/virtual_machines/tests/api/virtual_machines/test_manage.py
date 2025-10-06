"""Integration tests for starting and shutting off virtual machines.

Covers:
- Successful start / shut-off flows
- Invalid UUID / nonexistent VM errors
- Attempts to start an already-running VM or shut-off an already stopped VM
- Unauthorized access
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.libvirt.vm import (
    get_vms_state,
    get_vm_snapshots,
)
from openvair.libs.testing.utils import wait_for_field_value


def test_start_vm_success(
        client: TestClient, deactivated_virtual_machine: Dict
) -> None:
    """Test success starting shut-off VM and ensure it's added to libvirt."""
    vm_id = deactivated_virtual_machine['id']
    vm_name = deactivated_virtual_machine['name']

    response = client.post(f'/virtual-machines/{vm_id}/start/')
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['id'] == vm_id

    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'power_state', 'running'
    )

    vms_states = get_vms_state()
    assert vm_name in vms_states
    assert vms_states[vm_name] == 'running'

    vnc_resp = client.get(f'/virtual-machines/{vm_id}/vnc/')
    assert vnc_resp.status_code == status.HTTP_200_OK
    assert 'url' in vnc_resp.json()


def test_start_vm_already_running(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test attempt to start a VM that's already running."""
    vm_id = activated_virtual_machine['id']
    response = client.post(f'/virtual-machines/{vm_id}/start/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'power state' in response.text.lower()


def test_start_vm_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID format for start VM."""
    response = client.post('/virtual-machines/invalid-uuid/start/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_start_vm_nonexistent(client: TestClient) -> None:
    """Test starting a non-existent VM."""
    fake_id = str(uuid.uuid4())
    response = client.post(f'/virtual-machines/{fake_id}/start/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_start_vm_unauthorized(
        deactivated_virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Unauthorized request must return 401."""
    vm_id = deactivated_virtual_machine['id']
    response = unauthorized_client.post(f'/virtual-machines/{vm_id}/start/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_shut_off_vm_success(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test success shut off running VM and ensure it's removed from libvirt."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']

    response = client.post(f'/virtual-machines/{vm_id}/shut-off/')
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['id'] == vm_id

    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'power_state', 'shut_off'
    )

    vms_states = get_vms_state()
    assert vm_name not in vms_states


def test_shut_off_vm_already_shutoff(
        client: TestClient, deactivated_virtual_machine: Dict
) -> None:
    """Test attempt to shut off a VM that's already shut-off."""
    vm_id = deactivated_virtual_machine['id']
    response = client.post(f'/virtual-machines/{vm_id}/shut-off/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'power state' in response.text.lower()


def test_shut_off_vm_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID format for shut off VM."""
    response = client.post('/virtual-machines/invalid-uuid/shut-off/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_shut_off_vm_nonexistent(client: TestClient) -> None:
    """Test shut off for non-existent VM."""
    fake_id = str(uuid.uuid4())
    response = client.post(f'/virtual-machines/{fake_id}/shut-off/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_shut_off_vm_unauthorized(
        activated_virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Unauthorized request must return 401."""
    vm_id = activated_virtual_machine['id']
    response = unauthorized_client.post(f'/virtual-machines/{vm_id}/shut-off/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_vnc_vm_success(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test successful VNC access for running VM."""
    vm_id = activated_virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/vnc/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'url' in data
    assert data['url'] != ''


def test_vnc_vm_shutoff(
        client: TestClient, deactivated_virtual_machine: Dict
) -> None:
    """Test VNC access failure for shut off VM."""
    vm_id = deactivated_virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/vnc/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_vnc_vm_nonexistent(client: TestClient) -> None:
    """Test VNC access for nonexistent VM."""
    nonexistent_vm_id = str(uuid.uuid4())

    response = client.get(f'/virtual-machines/{nonexistent_vm_id}/vnc/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_vnc_vm_invalid_uuid(client: TestClient) -> None:
    """Test VNC access with invalid VM UUID format."""
    response = client.get('/virtual-machines/invalid-uuid/vnc/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_vnc_vm_unauthorized(
        activated_virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized VNC access attempt."""
    vm_id = activated_virtual_machine['id']

    response = unauthorized_client.get(f'/virtual-machines/{vm_id}/vnc/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_vm_restart_with_snapshot(
        client: TestClient, vm_snapshot: Dict, virtual_machine: Dict
) -> None:
    """Test that snapshots persist after VM shutdown and restart."""
    vm_id = virtual_machine['id']
    vm_name = virtual_machine['name']
    snapshot_name = vm_snapshot['name']

    initial_snapshot_response = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{vm_snapshot["id"]}'
    )
    assert initial_snapshot_response.status_code == status.HTTP_200_OK
    initial_snapshot = initial_snapshot_response.json()
    assert initial_snapshot['status'] == 'running'
    assert initial_snapshot['is_current'] is True
    initial_libvirt_snapshots, initial_current = get_vm_snapshots(vm_name)
    assert snapshot_name in initial_libvirt_snapshots
    assert initial_current == snapshot_name

    # Shut down VM
    shutdown_response = client.post(f'/virtual-machines/{vm_id}/shut-off/')
    assert shutdown_response.status_code == status.HTTP_201_CREATED
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'power_state', 'shut_off'
    )

    # Start VM again
    start_response = client.post(f'/virtual-machines/{vm_id}/start/')
    assert start_response.status_code == status.HTTP_201_CREATED
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'power_state', 'running'
    )

    restored_snapshot_response = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{vm_snapshot["id"]}'
    )
    assert restored_snapshot_response.status_code == status.HTTP_200_OK
    restored_snapshot = restored_snapshot_response.json()
    assert restored_snapshot['id'] == vm_snapshot['id']
    assert restored_snapshot['name'] == snapshot_name
    assert restored_snapshot['is_current'] is True
    assert restored_snapshot['vm_id'] == vm_id
    assert restored_snapshot['vm_name'] == vm_name
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{vm_snapshot["id"]}',
        'status',
        'running',
        timeout=120,
    )
    restored_libvirt_snapshots, restored_current = get_vm_snapshots(vm_name)
    assert snapshot_name in restored_libvirt_snapshots
    assert restored_current == snapshot_name
