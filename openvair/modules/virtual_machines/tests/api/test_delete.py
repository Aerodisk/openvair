"""Integration tests for virtual machines deletion.

Covers:
- Successful VM deletion
- Validation errors (e.g. invalid ID)
- Logical errors (e.g. running/non-existent VM, invalid status, with snapshots)
- Unauthorized access
"""

import uuid
from typing import Dict

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.libvirt.vm import get_vms_state
from openvair.libs.testing.utils import (
    wait_for_field_value,
    wait_full_deleting_object,
)
from openvair.modules.virtual_machines.service_layer.unit_of_work import (
    VMSqlAlchemyUnitOfWork,
)


def test_delete_vm_success(
        client: TestClient, deactivated_virtual_machine: Dict
) -> None:
    """Test successful deletion of a VM."""
    vm_id = deactivated_virtual_machine['id']
    vm_name = deactivated_virtual_machine['name']
    assert deactivated_virtual_machine['status'] == 'available'
    assert deactivated_virtual_machine['power_state'] == 'shut_off'

    response = client.delete(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == vm_id
    assert data['status'] == 'deleting'
    wait_full_deleting_object(client, '/virtual-machines/', vm_id)
    assert vm_name not in get_vms_state()
    with VMSqlAlchemyUnitOfWork() as uow:
        assert not uow.virtual_machines.get(vm_id)


def test_delete_vm_invalid_uuid(client: TestClient) -> None:
    """Test deletion attempt using invalid UUID format."""
    response = client.delete('/virtual-machines/not-a-valid-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_vm_running(
        client: TestClient, activated_virtual_machine: Dict
) -> None:
    """Test failure when trying to delete a running VM."""
    vm_id = activated_virtual_machine['id']
    vm_name = activated_virtual_machine['name']
    assert activated_virtual_machine['power_state'] == 'running'
    assert vm_name in get_vms_state()

    response = client.delete(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'power state' in response.text.lower()


def test_delete_vm_nonexistent(client: TestClient) -> None:
    """Test deletion attempt for non-existent VM."""
    non_existent_uuid = str(uuid.uuid4())
    response = client.delete(f'/virtual-machines/{non_existent_uuid}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


@pytest.mark.parametrize("invalid_status", ["creating", "starting"])
def test_delete_vm_invalid_statuses(
        client: TestClient,
        deactivated_virtual_machine: Dict,
        invalid_status: str
) -> None:
    """Test deletion attempts for VMs in various invalid statuses.

    Manually sets VM status in database to test deletion validation.
    """
    vm_id = deactivated_virtual_machine['id']
    with VMSqlAlchemyUnitOfWork() as uow:
        db_vm = uow.virtual_machines.get(vm_id)
        if db_vm:
            db_vm.status = invalid_status
            uow.commit()
    with VMSqlAlchemyUnitOfWork() as uow:
        db_vm = uow.virtual_machines.get(vm_id)
        if db_vm:
            assert db_vm.status == invalid_status

    response = client.delete(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'status' in response.text.lower()


def test_delete_vm_with_snapshots_success(
        client: TestClient, vm_snapshot: Dict
) -> None:
    """Test deletion of VM that has snapshots."""
    vm_id = vm_snapshot['vm_id']
    vm_name = vm_snapshot['vm_name']

    actual_vm = client.get(
        f'/virtual-machines/{vm_id}/'
    ).json()
    if actual_vm['power_state'] != 'shut_off':
        response = client.post(
            f'/virtual-machines/{vm_id}/shut-off/'
        ).json()
        wait_for_field_value(
            client,
            f'/virtual-machines/{response["id"]}/',
            'power_state',
            'shut_off',
        )

    delete_response = client.delete(f'/virtual-machines/{vm_id}/')
    assert delete_response.status_code == status.HTTP_200_OK
    data = delete_response.json()
    assert data['id'] == vm_id
    assert data['status'] == 'deleting'
    wait_full_deleting_object(client, '/virtual-machines/', vm_id)
    assert vm_name not in get_vms_state()
    with VMSqlAlchemyUnitOfWork() as uow:
        assert not uow.virtual_machines.get(vm_id)
        assert len(uow.snapshots.get_all_by_vm(vm_id)) == 0


def test_delete_vm_unauthorized(
        deactivated_virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized deletion attempt."""
    vm_id = deactivated_virtual_machine['id']
    response = unauthorized_client.delete(f'/virtual-machines/{vm_id}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
