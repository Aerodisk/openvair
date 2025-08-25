"""Shared fixtures for volume integration tests.

Provides:
- `cleanup_bridges`: Deletes all test bridges before and after test.
"""

from typing import Any, Generator

import pytest

from openvair.libs.log import get_logger
from openvair.libs.testing.utils import cleanup_test_bridges

LOG = get_logger(__name__)


@pytest.fixture
def cleanup_bridges() -> Generator[None, Any, None]:
    """Delete all test bridges before and after test."""
    cleanup_test_bridges()
    yield
    cleanup_test_bridges()
