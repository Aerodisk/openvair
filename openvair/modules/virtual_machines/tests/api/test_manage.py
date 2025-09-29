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

from openvair.libs.libvirt.vm import get_vms_state
from openvair.libs.testing.utils import wait_for_field_value


def test_start_vm_success(
        client: TestClient, deactivated_virtual_machine: Dict
) -> None:
    """Test success starting shut-off VM and ensure it's added to libvirt."""
    vm_id = deactivated_virtual_machine['id']
    vm_name = deactivated_virtual_machine['name']

    response = client.post(f'/virtual-machines/{vm_id}/start/')
    assert response.status_code == status.HTTP_201_CREATED, response.text
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
    assert response.status_code == status.HTTP_201_CREATED, response.text
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
