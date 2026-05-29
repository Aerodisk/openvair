"""Fixtures and configuration for the scheduler domain tests."""

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_cron_tab() -> Generator[MagicMock, None, None]:
    """Mock the system CronTab library.

    Ensures that CronTab can be used as a context manager and does not
    interact with the actual host operating system during tests.
    """
    with patch('openvair.modules.scheduler.domain.cron_jobs.cron_job.CronTab') as mock_cls: # noqa: E501
        mock_instance = mock_cls.return_value

        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None

        yield mock_instance
