"""Integration tests for virtual machine snapshots retrieval.

Covers:
- Getting all snapshots for a VM / specific snapshot by ID
- Logical errors (e.g. nonexistent VM, wrong VM ID).
- Unauthorized access
"""

import uuid
from typing import Dict, List

from fastapi import status
from fastapi.testclient import TestClient


def test_get_all_snapshots_success(
        client: TestClient, vm_snapshot: Dict, virtual_machine: Dict
) -> None:
    """Test retrieving all snapshots for a virtual machine."""
    vm_id = virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'snapshots' in data
    assert isinstance(data['snapshots'], List)
    assert len(data['snapshots']) == 1
    snapshot = data['snapshots'][0]
    expected_fields = [
        'id', 'name', 'description', 'vm_id', 'vm_name', 'parent',
        'created_at', 'is_current', 'status'
    ]
    assert all(field in snapshot for field in expected_fields)
    assert snapshot['id'] == vm_snapshot['id']
    assert snapshot['name'] == vm_snapshot['name']
    assert snapshot['description'] == vm_snapshot['description']
    assert snapshot['vm_id'] == vm_id
    assert snapshot['vm_name'] == virtual_machine['name']
    assert snapshot['status'] == 'running'
    assert snapshot['is_current'] is True
    assert snapshot['parent'] is None
    assert 'created_at' in snapshot


def test_get_snapshot_by_id_success(
        client: TestClient, vm_snapshot: Dict, virtual_machine: Dict
) -> None:
    """Test retrieving specific snapshot by ID."""
    vm_id = virtual_machine['id']
    snapshot_id = vm_snapshot['id']

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_fields = [
        'id', 'name', 'description', 'vm_id', 'vm_name', 'parent',
        'created_at', 'is_current', 'status'
    ]
    assert all(field in data for field in expected_fields)
    assert data['id'] == snapshot_id
    assert data['name'] == vm_snapshot['name']
    assert data['description'] == vm_snapshot['description']
    assert data['vm_id'] == vm_id
    assert data['vm_name'] == virtual_machine['name']
    assert data['status'] == 'running'
    assert data['is_current'] is True
    assert data['parent'] is None
    assert 'created_at' in data


def test_get_all_snapshots_empty_list_success(
        client: TestClient, virtual_machine: Dict
) -> None:
    """Test getting all snapshots when there are none."""
    vm_id = virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'snapshots' in data
    assert isinstance(data['snapshots'], List)
    assert len(data['snapshots']) == 0


def test_get_snapshot_nonexistent_vm(client: TestClient) -> None:
    """Test requesting snapshot for nonexistent VM ID."""
    nonexistent_vm_id = str(uuid.uuid4())
    snapshot_id = str(uuid.uuid4())

    response = client.get(
        f'/virtual-machines/{nonexistent_vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_get_snapshot_nonexistent_snapshot(
        client: TestClient, virtual_machine: Dict
) -> None:
    """Test requesting nonexistent snapshot ID."""
    vm_id = virtual_machine['id']
    nonexistent_snapshot_id = str(uuid.uuid4())

    response = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{nonexistent_snapshot_id}'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_get_snapshot_invalid_vm_uuid(client: TestClient) -> None:
    """Test invalid VM UUID format in path."""
    snapshot_id = str(uuid.uuid4())

    response = client.get(
        f'/virtual-machines/invalid-uuid/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_snapshot_invalid_snapshot_uuid(
        client: TestClient, virtual_machine: Dict
) -> None:
    """Test invalid snapshot UUID format in path."""
    vm_id = virtual_machine['id']

    response = client.get(f'/virtual-machines/{vm_id}/snapshots/invalid-uuid')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_snapshot_wrong_vm(
        client: TestClient, vm_snapshot: Dict
) -> None:
    """Test getting snapshot with correct ID but wrong VM ID."""
    wrong_vm_id = str(uuid.uuid4())
    snapshot_id = vm_snapshot['id']

    response = client.get(
        f'/virtual-machines/{wrong_vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'not found' in response.text.lower()


def test_get_all_snapshots_unauthorized(
        virtual_machine: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized request to get all snapshots."""
    vm_id = virtual_machine['id']

    response = unauthorized_client.get(f'/virtual-machines/{vm_id}/snapshots/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_snapshot_by_id_unauthorized(
        vm_snapshot: Dict,
        virtual_machine: Dict,
        unauthorized_client: TestClient,
) -> None:
    """Test unauthorized request to get specific snapshot."""
    vm_id = virtual_machine['id']
    snapshot_id = vm_snapshot['id']

    response = unauthorized_client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_id}'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
