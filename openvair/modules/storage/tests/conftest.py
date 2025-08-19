"""Fixtures for storage integration tests."""

from typing import Any, Generator

import pytest

from openvair.libs.testing.utils import cleanup_all_storages


@pytest.fixture(scope='function')
def cleanup_storages() -> Generator[None, Any, None]:
    """Cleanup all storages before and after test"""
    cleanup_all_storages()
    yield
    cleanup_all_storages()
