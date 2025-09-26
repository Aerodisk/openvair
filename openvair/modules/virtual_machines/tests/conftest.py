"""Fixtures for virtual machines integration tests.

Provides:
- `cleanup_vms`: Clean up all virtual machines before and after each test.
"""

from typing import Generator

import pytest

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    cleanup_all_volumes,
    cleanup_all_virtual_machines,
)

LOG = get_logger(__name__)

@pytest.fixture(scope='function', autouse=True)
def cleanup_vms() -> Generator:
    """Clean up all virtual machines before and after each test."""
    cleanup_all_virtual_machines()
    yield
    cleanup_all_virtual_machines()
    cleanup_all_volumes()
