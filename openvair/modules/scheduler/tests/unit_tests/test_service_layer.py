"""Unit tests for the scheduler service layer."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.modules.scheduler.service_layer.services import (
    SchedulerServiceLayerManager,
)
from openvair.modules.scheduler.service_layer.exceptions import (
    JobDependencyError,
)


def test_create_job_service_logic(mock_uow: MagicMock) -> None:
    """Проверка логики создания задачи в сервис-слое."""
    manager = SchedulerServiceLayerManager()
    manager.domain_rpc = MagicMock()

    data = {
        "name": "service_test_job",
        "cron_schedule": "*/5 * * * *",
        "command": "ls",
        "enabled": True
    }

    result = manager.create_job(data)

    assert result["name"] == "service_test_job"
    assert mock_uow.jobs.add.called
    assert mock_uow.commit.called
    assert manager.domain_rpc.call.called


def test_delete_job_service_logic(mock_uow: MagicMock) -> None:
    """Проверка логики удаления отключённой задачи в сервис-слое."""
    manager = SchedulerServiceLayerManager()
    manager.domain_rpc = MagicMock()

    job_id = uuid.uuid4()
    now = datetime(2024, 5, 28, 10, 45, 21)
    db_job = SchedulerJob(
        id=job_id,
        name='to_delete',
        description=None,
        cron_schedule='0 0 * * *',
        command='echo bye',
        enabled=False,
        created_at=now,
        updated_at=now,
    )
    mock_uow.jobs.get_by_id.return_value = db_job

    payload = {'id': job_id}
    result = manager.delete_job(payload)

    assert str(result['id']) == str(job_id)
    assert mock_uow.jobs.delete.called
    assert mock_uow.commit.called


def test_delete_enabled_job_raises_dependency_error(
    mock_uow: MagicMock,
) -> None:
    """Нельзя удалить включённую задачу без предварительного отключения."""
    manager = SchedulerServiceLayerManager()
    job_id = uuid.uuid4()
    mock_uow.jobs.get_by_id.return_value = MagicMock(id=job_id, enabled=True)

    with pytest.raises(JobDependencyError):
        manager.delete_job({'id': job_id})
