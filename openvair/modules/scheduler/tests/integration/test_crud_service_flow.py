"""Integration tests wiring SchedulerCRUD to SchedulerServiceLayerManager."""

import uuid
from typing import Any, Dict, Callable, Optional, cast
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.modules.scheduler.entrypoints.crud import SchedulerCRUD
from openvair.modules.scheduler.service_layer.services import (
    SchedulerServiceLayerManager,
)
from openvair.modules.scheduler.entrypoints.schemas.requests import (
    CreateJobRequest,
    UpdateJobRequest,
)


def _inline_rpc(
    manager: SchedulerServiceLayerManager,
) -> Callable[..., Any]:
    """Route CRUD RPC calls directly to the service-layer manager."""

    def _call(
        method_name: str,
        data_for_method: Optional[Dict[str, Any]] = None,
        **_kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        handler = getattr(manager, method_name)
        return handler(data_for_method or {})

    return _call


@pytest.fixture
def service_manager(mock_uow: MagicMock) -> SchedulerServiceLayerManager:
    """Service manager with mocked persistence and domain RPC."""
    manager = SchedulerServiceLayerManager()
    manager.domain_rpc = MagicMock()
    mock_uow.jobs.get_all.return_value = []
    return manager


@pytest.fixture
def wired_crud(
    service_manager: SchedulerServiceLayerManager,
) -> SchedulerCRUD:
    """CRUD adapter that invokes the service layer in-process."""
    crud = SchedulerCRUD()
    rpc_mock = MagicMock()
    rpc_mock.call.side_effect = _inline_rpc(service_manager)
    crud.service_layer_rpc = rpc_mock
    return crud


def test_create_job_crud_to_service_layer(
    wired_crud: SchedulerCRUD,
    service_manager: SchedulerServiceLayerManager,
    mock_uow: MagicMock,
) -> None:
    """POST flow: CRUD delegates create to service layer and domain RPC."""
    request = CreateJobRequest(
        name='integration_job',
        description=None,
        cron_schedule='0 12 * * *',
        command='echo integration',
        enabled=False,
    )

    result = wired_crud.create_job(request)

    assert result.name == 'integration_job'
    mock_uow.jobs.add.assert_called_once()
    domain_rpc = cast(MagicMock, service_manager.domain_rpc)
    domain_rpc.call.assert_called_once()
    call_kwargs = domain_rpc.call.call_args.kwargs
    assert call_kwargs['method_name'] == 'create'


def test_update_job_crud_to_service_layer(
    wired_crud: SchedulerCRUD,
    service_manager: SchedulerServiceLayerManager,
    mock_uow: MagicMock,
) -> None:
    """PATCH flow: CRUD delegates update to service layer."""
    job_id = uuid.uuid4()
    now = datetime(2024, 5, 28, 10, 45, 21)
    db_job = SchedulerJob(
        id=job_id,
        name='old_name',
        description=None,
        cron_schedule='0 1 * * *',
        command='echo old',
        enabled=False,
        created_at=now,
        updated_at=now,
    )
    mock_uow.jobs.get_by_id.return_value = db_job

    result = wired_crud.update_job(
        job_id,
        UpdateJobRequest(
            name='renamed_job',
            description=None,
            cron_schedule=None,
            command=None,
            enabled=None,
        ),
    )

    assert result.name == 'renamed_job'
    domain_rpc = cast(MagicMock, service_manager.domain_rpc)
    domain_rpc.call.assert_called_once()
    assert domain_rpc.call.call_args.kwargs['method_name'] == 'edit'


def test_delete_enabled_job_crud_returns_http_400(
    wired_crud: SchedulerCRUD,
    mock_uow: MagicMock,
) -> None:
    """DELETE on enabled job surfaces HTTP 400 via CRUD error translation."""
    job_id = uuid.uuid4()
    mock_uow.jobs.get_by_id.return_value = MagicMock(id=job_id, enabled=True)

    with pytest.raises(HTTPException) as exc_info:
        wired_crud.delete_job(job_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert 'enabled' in exc_info.value.detail.lower()
