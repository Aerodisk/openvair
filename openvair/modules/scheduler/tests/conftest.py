"""Pytest configuration and fixtures for the scheduler module tests."""

import os
import uuid
import datetime
from typing import Any, Dict, Optional, Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

LIVE_INFRA = os.environ.get('OPENVAIR_SCHEDULER_LIVE') == '1'

# Unit/API mocks; skipped when OPENVAIR_SCHEDULER_LIVE=1
if not LIVE_INFRA:
    patch('pika.BlockingConnection').start()
    patch('openvair.libs.messaging.messaging_agents.MessagingClient').start()
    patch('starlette.staticfiles.StaticFiles').start()


def _configure_uow_mock(instance: MagicMock) -> MagicMock:
    """Prepare a mocked SQLAlchemy unit-of-work for service-layer tests."""
    instance.__enter__.return_value = instance
    instance.__exit__.return_value = None
    instance.jobs.get_by_name.return_value = None

    def mock_refresh(obj: Any) -> None:  # noqa: ANN401
        if not getattr(obj, 'id', None):
            obj.id = uuid.uuid4()
        now = datetime.datetime.now()
        if getattr(obj, 'created_at', None) is None:
            obj.created_at = now
        if getattr(obj, 'updated_at', None) is None:
            obj.updated_at = now

    instance.session.refresh = mock_refresh
    return instance


@pytest.fixture
def anyio_backend() -> str:
    """Fixate the use of asyncio for anyio tests."""
    return 'asyncio'


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture for FastAPI TestClient with authorization override."""
    from openvair.main import app
    from openvair.libs.auth.jwt_utils import get_current_user

    def skip_auth() -> Dict[str, str]:
        return {"user_id": str(uuid.uuid4()), "role": "admin"}

    app.dependency_overrides[get_current_user] = skip_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_uow() -> Generator[Optional[MagicMock], None, None]:
    """Automatic Unit of Work mock for all tests in the module."""
    if LIVE_INFRA:
        yield None
        return

    with patch(
        'openvair.modules.scheduler.service_layer.services.SchedulerSqlAlchemyUnitOfWork'
    ) as mock:
        yield _configure_uow_mock(mock.return_value)


SAMPLE_JOB_ID = '74a18c88-04b7-4d6a-a50a-c91203b234db'


def sample_job_dict(**overrides: Any) -> Dict[str, Any]:  # noqa: ANN401
    """Minimal job payload compatible with JobResponse validation."""
    payload: Dict[str, Any] = {
        'id': SAMPLE_JOB_ID,
        'name': 'daily_backup',
        'description': 'System backup',
        'cron_schedule': '0 0 * * *',
        'command': '/usr/bin/backup',
        'enabled': True,
        'created_at': '2024-05-28T10:45:21Z',
        'updated_at': None,
        'last_run': None,
        'next_run': None,
    }
    payload.update(overrides)
    return payload
