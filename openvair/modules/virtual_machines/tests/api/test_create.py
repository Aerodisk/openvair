"""Integration tests for virtual machines creation.

Covers:
- Successful VM creation.
- Validation errors (e.g. missing fields, invalid config).
- Logical errors (e.g. duplicate name, nonexistent volume).
- Unauthorized access.
"""


import uuid
from typing import Dict, Union

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.libvirt.vm import get_vms_state
from openvair.libs.testing.utils import (
    wait_for_field_value,
    wait_for_field_not_empty,
)


def assert_vm_startup(client: TestClient, vm_id: str, vm_name: str) -> None:
    """Assert that VM can be successfully started and shut down.

    Args:
        client: TestClient instance
        vm_id: UUID of the virtual machine
        vm_name: Name of the virtual machine
    """
    start_response = client.post(f'/virtual-machines/{vm_id}/start/')
    assert start_response.status_code == status.HTTP_201_CREATED
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'power_state', 'running'
    )
    vms_states = get_vms_state()
    assert vm_name in vms_states
    assert vms_states[vm_name] == 'running'
    vnc_response = client.get(f'/virtual-machines/{vm_id}/vnc/')
    assert vnc_response.status_code == status.HTTP_200_OK
    vnc_data = vnc_response.json()
    assert 'url' in vnc_data
    shutdown_response = client.post(f'/virtual-machines/{vm_id}/shut-off/')
    assert shutdown_response.status_code == status.HTTP_201_CREATED
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'status', 'available'
    )
    wait_for_field_value(
        client, f'/virtual-machines/{vm_id}/', 'power_state', 'shut_off'
    )
    vms_states = get_vms_state()
    assert vm_name not in vms_states


def test_create_vm_success(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test successful virtual machine creation."""
    response = client.post(
        '/virtual-machines/create/',
        json=vm_create_data
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    assert 'id' in data
    assert data['name'] == vm_create_data['name']
    assert data['description'] == vm_create_data['description']

    wait_for_field_value(
        client, f'/virtual-machines/{data["id"]}/', 'status', 'available'
    )
    assert_vm_startup(client, data["id"], data["name"])


def test_create_vm_auto_volume_success(
        client: TestClient, volume: Dict, vm_create_data: Dict
) -> None:
    """Test successful VM creation with auto-created volume."""
    vm_data = {
        **vm_create_data,
        "disks": {
            "attach_disks": [
                {
                    "name": "test_auto_created",
                    "format": "qcow2",
                    "emulation": "virtio",
                    "storage_id": volume["storage_id"],
                    "size": 1000000000,
                    "read_only": False,
                    "qos": {
                        "iops_read": 500,
                        "iops_write": 500,
                        "mb_read": 150,
                        "mb_write": 100
                    },
                    "boot_order": 1,
                    "order": 1,
                }
            ]
        },
    }

    response = client.post(
        '/virtual-machines/create/', json=vm_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    wait_for_field_not_empty(
        client, f'/virtual-machines/{data["id"]}', 'disks'
    )
    assert_vm_startup(client, data["id"], data["name"])


def test_create_vm_missing_fields(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test VM creation with missing required fields."""
    required_fields = [
        'name',
        'os',
        'cpu',
        'ram',
        'graphic_interface',
        'disks',
        'virtual_interfaces'
    ]

    for field in required_fields:
        vm_create_data.pop(field)
        response = client.post('/virtual-machines/create/', json=vm_create_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_vm_duplicate_name(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test VM creation with duplicate name."""
    response_1 = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response_1.status_code == status.HTTP_201_CREATED

    response_2 = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response_2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_vm_nonexistent_volume(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test VM creation with nonexistent volume_id."""
    vm_create_data["disks"]["attach_disks"][0]["volume_id"] = str(uuid.uuid4())

    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'volume' in response.text.lower()


def test_create_vm_invalid_graphic_interface(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test VM creation with invalid graphic interface type."""
    vm_create_data['graphic_interface']['connect_type'] = 'invalid_connect_type'

    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("field,value", [
    ("cores", 0),
    ("threads", 0),
    ("sockets", 0),
    ("type", "wrong_type"),
    ("model", "wrong_model"),
])
def test_create_vm_invalid_cpu(
        client: TestClient,
        vm_create_data: Dict,
        field: str,
        value: Union[int, str],
) -> None:
    """Test VM creation with invalid CPU configuration."""
    vm_create_data['cpu'][field] = value
    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("ram_size", [-1, 0])
def test_create_vm_invalid_ram(
        client: TestClient, vm_create_data: Dict, ram_size: int
) -> None:
    """Test VM creation with invalid RAM size."""
    vm_create_data['ram']['size'] = ram_size
    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("field,value", [
    ("boot_device", "wrong_boot_device"),
    ("bios", "wrong_bios"),
    ("graphic_driver", "wrong_graphic_driver"),
])
def test_create_vm_invalid_os(
        client: TestClient, vm_create_data: Dict, field: str, value: str
) -> None:
    """Test VM creation with invalid OS configuration."""
    vm_create_data['os'][field] = value
    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_vm_invalid_mac(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test VM creation with invalid MAC address format."""
    vm_create_data['virtual_interfaces'][0]['mac'] = 'bad_mac'

    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("field,value", [
    ("model", "wrong_model"),
    ("mac", "wrong_mac"),
    ("interface", ""),
])
def test_create_vm_invalid_virtual_interface(
        client: TestClient, vm_create_data: Dict, field: str, value: str
) -> None:
    """Test VM creation with invalid virtual network interface."""
    vm_create_data['virtual_interfaces'][0][field] = value
    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("field,value", [
    ("format", "wrong_format"),
    ("emulation", "wrong_emulation"),
])
def test_create_vm_invalid_disks(
        client: TestClient, vm_create_data: Dict, field: str, value: str
) -> None:
    """Test VM creation with invalid disk configuration."""
    vm_create_data['disks']['attach_disks'][0][field] = value
    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("invalid_name", [str("a" * 256), ""])
def test_create_vm_invalid_name(
        client: TestClient, vm_create_data: Dict, invalid_name: str,
) -> None:
    """Test VM creation with invalid name size."""
    vm_create_data['name'] = invalid_name
    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_vm_empty_disks(
        client: TestClient, vm_create_data: Dict
) -> None:
    """Test VM creation without any disks attached."""
    vm_create_data['disks']['attach_disks'] = []

    response = client.post('/virtual-machines/create/', json=vm_create_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_vm_unauthorized(
        vm_create_data: Dict, unauthorized_client: TestClient
) -> None:
    """Test unauthorized request."""
    response = unauthorized_client.post(
        '/virtual-machines/create/',
        json=vm_create_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
