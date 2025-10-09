"""Integration tests for editing virtual machines.

Covers:
- Successful VM edit (metadata / new disk).
- Validation errors (invalid UUID, invalid input data).
- Logical errors (running vm, duplicate name).
- Unauthorized access.
"""

import uuid
from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import (
    wait_for_field_value,
    generate_test_entity_name,
)


def test_edit_vm_success(
    client: TestClient, vm_edit_data: Dict, virtual_machine: Dict
) -> None:
    """Test successful VM metadata edit."""
    vm_id = virtual_machine['id']
    assert vm_edit_data['name'] != virtual_machine['name']
    assert vm_edit_data['description'] != virtual_machine['description']
    response = client.post(
        f'/virtual-machines/{vm_id}/edit/', json=vm_edit_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'status',
        'available',
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'name',
        vm_edit_data['name'],
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'description',
        vm_edit_data['description'],
    )


def test_edit_vm_add_disk_success(
    client: TestClient,
    vm_edit_data: Dict,
    storage: Dict,
    virtual_machine: Dict,
) -> None:
    """Test successful VM edit with new volume as disk attachment."""
    volume_data = {
        'name': generate_test_entity_name('volume'),
        'description': 'Additional volume for VM edit test',
        'storage_id': storage['id'],
        'format': 'qcow2',
        'size': 2048,
        'read_only': False,
    }
    volume_response = client.post('/volumes/create/', json=volume_data)
    assert volume_response.status_code == status.HTTP_200_OK
    new_volume = volume_response.json()
    vm_id = virtual_machine['id']
    edit_data = {
        **vm_edit_data,
        'disks': {
            'attach_disks': [
                {
                    'volume_id': new_volume['id'],
                    'qos': {
                        'iops_read': 500,
                        'iops_write': 500,
                        'mb_read': 150,
                        'mb_write': 150,
                    },
                    'boot_order': 2,
                    'order': 2,
                    'read_only': False,
                }
            ],
            'detach_disks': [],
            'edit_disks': [],
        },
    }

    response = client.post(f'/virtual-machines/{vm_id}/edit/', json=edit_data)
    assert response.status_code == status.HTTP_201_CREATED
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    vm_after_edit = client.get(f'/virtual-machines/{vm_id}/').json()
    assert len(vm_after_edit['disks']) == 1 + 1


def test_edit_vm_invalid_uuid(client: TestClient, vm_edit_data: Dict) -> None:
    """Test VM edit with invalid UUID."""
    response = client.post(
        '/virtual-machines/invalid-uuid/edit/', json=vm_edit_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_vm_nonexistent(client: TestClient, vm_edit_data: Dict) -> None:
    """Test editing non-existent VM."""
    fake_id = str(uuid.uuid4())
    response = client.post(
        f'/virtual-machines/{fake_id}/edit/', json=vm_edit_data
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_edit_vm_invalid_payload(
    client: TestClient, virtual_machine: Dict
) -> None:
    """Test VM edit with invalid payload."""
    vm_id = virtual_machine['id']
    vm_edit_payload = {'name': ''}
    response = client.post(
        f'/virtual-machines/{vm_id}/edit/', json=vm_edit_payload
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_edit_vm_running(
    client: TestClient,
    vm_edit_data: Dict,
    activated_virtual_machine: Dict,
) -> None:
    """Test editing VM in 'running' power_state."""
    vm_id = activated_virtual_machine['id']

    response = client.post(
        f'/virtual-machines/{vm_id}/edit/', json=vm_edit_data
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_edit_vm_duplicate_name(
    client: TestClient,
    vm_create_data: Dict,
    vm_edit_data: Dict,
) -> None:
    """Test renaming VM to a name that already exists."""
    response1 = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response1.status_code == status.HTTP_201_CREATED
    vm1 = response1.json()
    wait_for_field_value(
        client, f'/virtual-machines/{vm1["id"]}/', 'status', 'available'
    )
    vm2_payload = {**vm_create_data, 'name': generate_test_entity_name('vm')}
    response2 = client.post('/virtual-machines/create/', json=vm2_payload)
    assert response2.status_code == status.HTTP_201_CREATED
    vm2 = response2.json()
    wait_for_field_value(
        client, f'/virtual-machines/{vm2["id"]}/', 'status', 'available'
    )

    vm_edit_payload = {**vm_edit_data, 'name': vm1['name']}
    response_edit = client.post(
        f"/virtual-machines/{vm2['id']}/edit/", json=vm_edit_payload
    )
    assert response_edit.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_edit_vm_unauthorized(
    vm_edit_data: Dict,
    virtual_machine: Dict,
    unauthorized_client: TestClient,
) -> None:
    """Unauthorized request on edit VM."""
    vm_id = virtual_machine['id']
    response = unauthorized_client.post(
        f'/virtual-machines/{vm_id}/edit/', json=vm_edit_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
