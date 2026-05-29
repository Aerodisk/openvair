"""Live E2E checks against PostgreSQL, RabbitMQ, and HTTP API.

Skipped automatically when infrastructure is unavailable.
Run explicitly:
  pytest openvair/modules/scheduler/tests/integration/test_live_e2e.py -v
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Generator, cast

import httpx
import pytest
from fastapi import status
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from openvair.modules.scheduler.config import (
    DATABASE_URL,
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.scheduler.adapters.orm import Base
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.scheduler.service_layer.services import (
    SchedulerServiceLayerManager,
)

LIVE_API_BASE = 'http://127.0.0.1:8000'
TEST_JOB_PREFIX = 'e2e_scheduler_'


def _db_available() -> bool:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        engine.dispose()
    except (OSError, SQLAlchemyError):
        return False
    else:
        return True


def _api_available() -> bool:
    try:
        response = httpx.get(f'{LIVE_API_BASE}/docs', timeout=3.0)
    except (OSError, httpx.HTTPError):
        return False
    else:
        return response.status_code == status.HTTP_200_OK


def _rpc_available() -> bool:
    try:
        client = MessagingClient(queue_name=API_SERVICE_LAYER_QUEUE_NAME)
        result = client.call(
            SchedulerServiceLayerManager.get_all_jobs.__name__,
            data_for_method={},
        )
        return isinstance(result, list)
    except (OSError, Exception):
        return False


pytestmark = [
    pytest.mark.integration,
    pytest.mark.live,
]


@pytest.fixture(scope='module')
def db_session() -> Generator[Session, None, None]:
    """SQLAlchemy session bound to the live PostgreSQL database."""
    if not _db_available():
        pytest.skip('PostgreSQL is not reachable')
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture(scope='module')
def api_token() -> str:
    """Obtain JWT for authenticated scheduler API calls."""
    if not _api_available():
        pytest.skip('HTTP API is not reachable on port 8000')
    response = httpx.post(
        f'{LIVE_API_BASE}/auth/',
        data={'username': 'sasha', 'password': 'sasha'},
        timeout=10.0,
    )
    if response.status_code != status.HTTP_200_OK:
        pytest.skip(f'Auth failed: {response.status_code} {response.text}')
    return cast(str, response.json()['access_token'])


def _unique_job_name() -> str:
    return f'{TEST_JOB_PREFIX}{uuid.uuid4().hex[:12]}'


def _cleanup_jobs_by_prefix(session: Session) -> None:
    session.execute(
        text(
            "DELETE FROM scheduler_jobs WHERE name LIKE :prefix"
        ),
        {'prefix': f'{TEST_JOB_PREFIX}%'},
    )
    session.commit()


@pytest.fixture(autouse=True)
def cleanup_e2e_jobs(db_session: Session) -> Generator[None, None, None]:
    """Remove E2E jobs before and after each test."""
    _cleanup_jobs_by_prefix(db_session)
    yield
    _cleanup_jobs_by_prefix(db_session)


@pytest.mark.skipif(not _db_available(), reason='PostgreSQL is not reachable')
def test_live_service_layer_full_stack() -> None:
    """Service layer + domain RPC + DB (in-process, not systemd)."""
    manager = SchedulerServiceLayerManager()
    manager.domain_rpc = MessagingClient(
        queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
    )
    name = _unique_job_name()
    payload: Dict[str, Any] = {
        'name': name,
        'description': 'live service layer',
        'cron_schedule': '30 7 * * *',
        'command': 'echo openvair_live',
        'enabled': False,
    }

    created = manager.create_job(payload)
    assert created['name'] == name
    job_id = created['id']

    jobs = manager.get_all_jobs()
    assert any(item['name'] == name for item in jobs)

    manager.delete_job({'id': job_id})


def _systemd_services_updated() -> bool:
    """True when domain listens on the contract queue (post-fix deploy)."""
    try:
        import pika

        conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        ch = conn.channel()
        ch.queue_declare(queue='scheduler_service_layer_domain', passive=True)
        conn.close()
    except (OSError, Exception):
        return False
    else:
        return True


@pytest.mark.skipif(
    not _systemd_services_updated(),
    reason=(
        'Restart scheduler-domain.service so it binds to '
        'scheduler_service_layer_domain'
    ),
)
@pytest.mark.skipif(
    not _rpc_available(),
    reason='RabbitMQ / service layer RPC unavailable',
)
def test_live_rpc_create_list_delete() -> None:
    """Full job lifecycle through systemd service-layer RPC."""
    client = MessagingClient(queue_name=API_SERVICE_LAYER_QUEUE_NAME)
    name = _unique_job_name()
    payload: Dict[str, Any] = {
        'name': name,
        'description': 'live e2e',
        'cron_schedule': '0 6 * * *',
        'command': 'echo openvair_e2e',
        'enabled': False,
    }

    created = client.call(
        SchedulerServiceLayerManager.create_job.__name__,
        data_for_method=payload,
    )
    assert created['name'] == name
    job_id = created['id']

    jobs = client.call(
        SchedulerServiceLayerManager.get_all_jobs.__name__,
        data_for_method={},
    )
    assert any(item['name'] == name for item in jobs)

    deleted = client.call(
        SchedulerServiceLayerManager.delete_job.__name__,
        data_for_method={'id': job_id},
    )
    assert deleted['id'] == job_id

    enabled_name = _unique_job_name()
    enabled_payload = {**payload, 'name': enabled_name, 'enabled': True}
    enabled_job = client.call(
        SchedulerServiceLayerManager.create_job.__name__,
        data_for_method=enabled_payload,
    )
    enabled_id = enabled_job['id']

    with pytest.raises(Exception) as exc_info:
        client.call(
            SchedulerServiceLayerManager.delete_job.__name__,
            data_for_method={'id': enabled_id},
        )
    assert 'enabled' in str(exc_info.value).lower()

    client.call(
        SchedulerServiceLayerManager.edit_job.__name__,
        data_for_method={'id': enabled_id, 'enabled': False},
    )
    client.call(
        SchedulerServiceLayerManager.delete_job.__name__,
        data_for_method={'id': enabled_id},
    )


@pytest.mark.skipif(not _api_available(), reason='HTTP API unavailable')
def test_live_api_crud_flow(api_token: str, db_session: Session) -> None:
    """Scheduler REST API against running openvair.main."""
    headers = {'Authorization': f'Bearer {api_token}'}
    name = _unique_job_name()
    create_body = {
        'name': name,
        'description': 'api e2e',
        'cron_schedule': '15 4 * * *',
        'command': 'echo api_e2e',
        'enabled': False,
    }

    with httpx.Client(
        base_url=LIVE_API_BASE,
        headers=headers,
        timeout=30.0,
    ) as client:
        create_resp = client.post('/scheduler/jobs', json=create_body)
        assert create_resp.status_code == status.HTTP_201_CREATED, (
            create_resp.text
        )
        job = create_resp.json()['data']
        job_id = job['id']
        assert job['name'] == name

        list_resp = client.get('/scheduler/jobs')
        assert list_resp.status_code == status.HTTP_200_OK, list_resp.text
        items = list_resp.json()['data']['items']
        assert any(item['name'] == name for item in items)

        get_resp = client.get(f'/scheduler/jobs/{job_id}')
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.json()['data']['id'] == job_id

        patch_resp = client.patch(
            f'/scheduler/jobs/{job_id}',
            json={'description': 'updated'},
        )
        assert patch_resp.status_code == status.HTTP_200_OK
        assert patch_resp.json()['data']['description'] == 'updated'

        delete_resp = client.delete(f'/scheduler/jobs/{job_id}')
        assert delete_resp.status_code == status.HTTP_200_OK, (
            delete_resp.text
        )

    row = db_session.execute(
        text('SELECT id FROM scheduler_jobs WHERE id = :id'),
        {'id': job_id},
    ).first()
    assert row is None


def test_live_db_scheduler_jobs_table_exists(db_session: Session) -> None:
    """scheduler_jobs table is present in PostgreSQL."""
    result = db_session.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'scheduler_jobs'"
        )
    ).fetchall()
    columns = {row[0] for row in result}
    assert 'cron_schedule' in columns
    assert 'enabled' in columns
