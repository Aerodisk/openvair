"""Fixtures for virtual machines integration tests.

Provides:
- `cleanup_vms`: Clean up all virtual machines before and after each test.
"""
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    create_resource,
    cleanup_all_images,
    cleanup_all_volumes,
    cleanup_all_storages,
    wait_for_field_value,
    cleanup_all_templates,
    generate_test_entity_name,
    cleanup_all_virtual_machines,
)

LOG = get_logger(__name__)

@pytest.fixture(scope='function', autouse=True)
def cleanup_vms() -> Generator:
    """Clean up all virtual machines before and after each test."""
    cleanup_all_virtual_machines()
    cleanup_all_images()
    cleanup_all_volumes()
    cleanup_all_templates()
    cleanup_all_storages()
    yield
    cleanup_all_virtual_machines()
    cleanup_all_images()
    cleanup_all_volumes()
    cleanup_all_templates()
    cleanup_all_storages()


@pytest.fixture(scope='function')
def vm_snapshot(
        client: TestClient, activated_virtual_machine: Dict
) -> Generator[Dict, None, None]:
    """Creates a snapshot in activated (running) VM."""
    vm_id = activated_virtual_machine['id']
    snapshot_data = {
        "name": generate_test_entity_name('snapshot'),
        "description": "Test snapshot",
    }
    snapshot_info = create_resource(
        client,
        f'/virtual-machines/{vm_id}/snapshots/',
        snapshot_data,
        'snapshot',
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_info["id"]}',
        'status',
        'running',
        timeout=120,
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_info["id"]}',
        'is_current',
        expected=True,
        timeout=120
    )
    wait_for_field_value(
        client,
        f'/virtual-machines/{vm_id}/',
        'power_state',
        'running',
        timeout=120,
    )
    snapshot = client.get(
        f'/virtual-machines/{vm_id}/snapshots/{snapshot_info["id"]}'
    ).json()

    yield snapshot
