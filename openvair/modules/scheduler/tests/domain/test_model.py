"""Unit tests for the scheduler domain models and factories."""

from unittest.mock import MagicMock, patch

import pytest

from openvair.modules.scheduler.domain.base import BaseScheduler
from openvair.modules.scheduler.domain.model import SchedulerFactory
from openvair.modules.scheduler.domain.cron_jobs.cron_job import (
    CronJobScheduler,
)


@patch('openvair.modules.scheduler.domain.model.CronTab')
def test_scheduler_factory_get_system_cron(mock_crontab_cls: MagicMock) -> None:
    """Test that the factory returns a CronJobScheduler for 'system_cron'.

    The CronTab class is mocked to prevent the factory from executing
    privileged OS commands (like `crontab -u root`) during testing.
    """
    factory = SchedulerFactory()
    scheduler_data = {'type': 'system_cron', 'user': 'root'}

    scheduler = factory.get_scheduler(scheduler_data)

    assert isinstance(scheduler, BaseScheduler)
    assert isinstance(scheduler, CronJobScheduler)
    mock_crontab_cls.assert_called_once_with(user='root')


def test_scheduler_factory_unknown_type() -> None:
    """Test that the factory raises an error for unknown scheduler types."""
    factory = SchedulerFactory()
    scheduler_data = {'type': 'unknown_scheduler_type'}

    with pytest.raises(Exception) as exc_info:
        factory.get_scheduler(scheduler_data)

    assert exc_info.value is not None


def test_scheduler_factory_registered_types() -> None:
    """Test that 'system_cron' is correctly registered in the factory."""
    registered_schedulers = getattr(SchedulerFactory, '_schedulers', {})

    if registered_schedulers:
        assert 'system_cron' in registered_schedulers
        assert registered_schedulers['system_cron'] is CronJobScheduler
