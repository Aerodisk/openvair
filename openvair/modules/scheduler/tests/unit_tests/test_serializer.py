"""Unit tests for scheduler ORM serializers."""

import uuid
from datetime import datetime

from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.modules.scheduler.adapters.serializer import (
    SchedulerJobSerializer,
    ApiSchedulerJobSerializer,
    CreateSchedulerJobSerializer,
    DomainSchedulerJobSerializer,
)


def _sample_orm_job() -> SchedulerJob:
    job_id = uuid.uuid4()
    now = datetime(2024, 5, 28, 10, 45, 21)
    return SchedulerJob(
        id=job_id,
        name='backup_daily',
        description='Nightly backup',
        cron_schedule='0 3 * * *',
        command='/usr/bin/backup',
        enabled=True,
        created_at=now,
        updated_at=now,
        last_run=None,
        next_run=None,
    )


def test_api_serializer_round_trip() -> None:
    """ApiSchedulerJobSerializer preserves job fields."""
    source = _sample_orm_job()
    dto = ApiSchedulerJobSerializer.to_dto(source)
    restored = ApiSchedulerJobSerializer.to_orm(dto)

    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.cron_schedule == source.cron_schedule


def test_domain_serializer_payload_subset() -> None:
    """Domain serializer exposes only RPC-relevant fields."""
    source = _sample_orm_job()
    payload = DomainSchedulerJobSerializer.to_dict(source)

    assert set(payload.keys()) == {
        'id',
        'name',
        'description',
        'cron_schedule',
        'command',
        'enabled',
    }
    assert payload['name'] == 'backup_daily'


def test_create_serializer_from_dict() -> None:
    """Create serializer builds ORM entity from validated dict."""
    job = CreateSchedulerJobSerializer.from_dict(
        {
            'name': 'new_job',
            'cron_schedule': '*/10 * * * *',
            'command': 'echo test',
            'enabled': False,
        }
    )
    assert job.name == 'new_job'
    assert job.enabled is False


def test_facade_matches_typed_serializers() -> None:
    """SchedulerJobSerializer facade delegates to typed serializers."""
    source = _sample_orm_job()

    assert SchedulerJobSerializer.to_web(source) == (
        ApiSchedulerJobSerializer.to_dict(source)
    )
    assert SchedulerJobSerializer.to_domain(source) == (
        DomainSchedulerJobSerializer.to_dict(source)
    )
