"""Integration tests for virtual machines retrieval.

Covers:
- Getting all VMs with pagination.
- Getting specific VM by ID.
- Handling errors for invalid or nonexistent VM IDs.
- Unauthorized access.
"""

import uuid
from typing import Dict, List

from fastapi import status
from fastapi.testclient import TestClient


def test_get_all_vms_success(client: TestClient, virtual_machine: Dict) -> None:
    """Test retrieving all virtual machines.

    Asserts:
    - VM under test is present in results
    - Pagination structure is correct
    """
    response = client.get('/virtual-machines/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    fields = ['items', 'total', 'page', 'size']
    assert all(field in data for field in fields)
    assert isinstance(data['items'], List)
    assert data['total'] == 1
    assert len(data['items']) == 1
    assert any(vm['id'] == virtual_machine['id'] for vm in data['items'])


def test_get_vm_by_id_success(
    client: TestClient, virtual_machine: Dict
) -> None:
    """Test retrieving specific VM by ID returns correct data."""
    vm_id = virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == vm_id
    assert data['name'] == virtual_machine['name']
    assert data['description'] == virtual_machine['description']
    fields = [
        'cpu',
        'ram',
        'os',
        'disks',
        'virtual_interfaces',
        'graphic_interface',
        'status',
        'power_state',
    ]
    assert all(field in data for field in fields)


def test_get_vm_validate_structure_success(
    client: TestClient, virtual_machine: Dict
) -> None:
    """Test that returned VM data matches expected schema structure."""
    vm_id = virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    vm_fields = [
        'id',
        'name',
        'status',
        'power_state',
        'description',
        'information',
    ]
    assert all(field in data for field in vm_fields)

    cpu_fields = ['cores', 'threads', 'sockets', 'model', 'type']
    assert all(field in data['cpu'] for field in cpu_fields)
    assert 'size' in data['ram']
    os_fields = ['boot_device', 'bios', 'graphic_driver']
    assert all(field in data['os'] for field in os_fields)
    assert isinstance(data['disks'], List)
    disk_fields = ['id', 'order', 'boot_order']
    assert all(field in data['disks'][0] for field in disk_fields)
    assert isinstance(data['virtual_interfaces'], List)
    interface_fields = ['id', 'mode', 'model', 'mac', 'interface']
    assert all(
        field in data['virtual_interfaces'][0] for field in interface_fields
    )
    assert 'connect_type' in data['graphic_interface']


def test_get_all_vms_empty_list_success(client: TestClient) -> None:
    """Test getting all VMs when there are none."""
    response = client.get('/virtual-machines/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    fields = ['items', 'total', 'page', 'size']
    assert all(field in data for field in fields)
    assert isinstance(data['items'], List)
    assert data['total'] == 0
    assert len(data['items']) == 0


def test_get_all_vms_with_pagination(
    client: TestClient,
    virtual_machine: Dict,
) -> None:
    """Test that pagination metadata is returned correctly for VMs list."""
    response = client.get('/virtual-machines/?page=1&size=1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    fields = ['items', 'total', 'page', 'size']
    assert all(field in data for field in fields)
    assert data['page'] == 1
    assert data['size'] == 1
    assert any(vm['id'] == virtual_machine['id'] for vm in data['items'])


def test_get_nonexistent_vm_by_id(client: TestClient) -> None:
    """Test requesting nonexistent VM ID returns appropriate error."""
    fake_id = str(uuid.uuid4())

    response = client.get(f'/virtual-machines/{fake_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_get_vm_invalid_uuid(client: TestClient) -> None:
    """Test invalid UUID format in path returns HTTP 422."""
    response = client.get('/virtual-machines/invalid-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_vms_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized request to get all VMs returns 401."""
    response = unauthorized_client.get('/virtual-machines/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_vm_by_id_unauthorized(
    virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized request to get specific VM returns 401."""
    vm_id = virtual_machine['id']
    response = unauthorized_client.get(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
