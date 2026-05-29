"""Tests for scheduler API endpoints."""

from uuid import uuid4
from unittest.mock import Mock, AsyncMock

import pytest


@pytest.mark.anyio
async def test_get_jobs_success(mocker: AsyncMock) -> None:
    """Тест асинхронного получения всех задач"""
    from openvair.modules.scheduler.entrypoints import api as scheduler_api

    crud = Mock()
    fake_jobs = [Mock()]

    mocker.patch.object(
        scheduler_api,
        "run_in_threadpool",
        new=AsyncMock(return_value=fake_jobs),
    )

    mocker.patch.object(
        scheduler_api,
        "paginate",
        return_value=Mock(),
    )

    result = await scheduler_api.get_jobs(crud=crud, params=Mock())
    assert result.status == "success"

@pytest.mark.anyio
async def test_get_job_success(mocker: AsyncMock) -> None:
    """Тест асинхронного получения задачи по ID"""
    from openvair.modules.scheduler.entrypoints import api as scheduler_api

    job_id = uuid4()
    crud = Mock()
    fake_job = Mock()

    mocker.patch.object(
        scheduler_api,
        "run_in_threadpool",
        new=AsyncMock(return_value=fake_job),
    )

    result = await scheduler_api.get_job(job_id=job_id, crud=crud)
    assert result.status == "success"
    assert result.data is fake_job
