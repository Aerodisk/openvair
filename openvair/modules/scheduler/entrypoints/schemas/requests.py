"""Request models for scheduler API operations.

These schemas are request bodies for scheduler HTTP endpoints. They extend
domain DTOs with OpenAPI metadata (titles, descriptions, examples) shown in
Swagger.

Classes:
    RequestCreateJob: body for ``POST /scheduler/jobs``.
    RequestUpdateJob: body for ``PATCH /scheduler/jobs/{job_id}``.
    CreateJobRequest: RDE contract alias for ``RequestCreateJob``.
    UpdateJobRequest: RDE contract alias for ``RequestUpdateJob``.
"""

from typing import Any, Optional

from pydantic import Field, ConfigDict

from openvair.common.base_pydantic_models import APIConfigRequestModel
from openvair.modules.scheduler.adapters.dto.internal.models import (
    CreateJobDomainDTO,
    UpdateJobDomainDTO,
)

_DESC_JOB_NAME = (
    'Unique job name (1-50 characters). Used as the cron comment label and '
    'must not collide with another job in the scheduler.'
)

_DESC_JOB_DESCRIPTION = (
    'Human-readable note stored in the database only; not passed to cron.'
)

_DESC_CRON = (
    'Five-field cron expression: minute hour day-of-month month '
    'day-of-week. Example: ``0 3 * * *`` runs every day at 03:00; '
    '``*/5 * * * *`` runs every five minutes. Sub-minute schedules are '
    'not supported.'
)

_DESC_COMMAND = (
    'Command line executed by the OS cron daemon under '
    '``scheduler.cron_user`` from project_config.toml. Must be non-empty. '
    'Blocked utilities include rm -rf, dd, mkfs, curl, and wget. Allowed '
    'characters: letters, digits, and ``_-./ >&|;\'"*``. Shell '
    'substitution (for example ``$()`` or backticks) is rejected.'
)

_DESC_ENABLED_CREATE = (
    'When true (default), the job is written to the database and a crontab '
    'entry is created immediately. When false, only the database record is '
    'kept until the job is enabled via PATCH.'
)

_DESC_ENABLED_UPDATE = (
    'Set to false before DELETE: an enabled job cannot be removed (HTTP '
    '409). Toggling updates both the database and the crontab entry.'
)

_CREATE_BODY_EXAMPLE: dict[str, Any] = {
    'name': 'backup_daily',
    'description': 'Daily database backup',
    'cron_schedule': '0 3 * * *',
    'command': 'backup.sh >> /var/log/openvair-backup.log 2>&1',
    'enabled': True,
}

_UPDATE_BODY_EXAMPLE: dict[str, Any] = {
    'cron_schedule': '0 2 * * *',
    'enabled': False,
}


class RequestCreateJob(CreateJobDomainDTO, APIConfigRequestModel):
    """Request body for creating a scheduled job.

    Validated fields are persisted and, when ``enabled`` is true, registered
    in the system crontab for the configured cron user.
    """

    model_config = ConfigDict(
        json_schema_extra={'examples': [_CREATE_BODY_EXAMPLE]},
    )

    name: str = Field(
        ...,
        title='Job name',
        examples=['backup_daily'],
        description=_DESC_JOB_NAME,
        min_length=1,
        max_length=50,
    )
    description: Optional[str] = Field(
        None,
        title='Description',
        examples=['Daily database backup job'],
        description=_DESC_JOB_DESCRIPTION,
        max_length=255,
    )
    cron_schedule: str = Field(
        ...,
        title='Cron schedule',
        examples=['0 3 * * *'],
        description=_DESC_CRON,
    )
    command: str = Field(
        ...,
        title='Command',
        examples=['backup.sh >> /var/log/openvair-backup.log 2>&1'],
        description=_DESC_COMMAND,
        min_length=1,
    )
    enabled: bool = Field(
        default=True,
        title='Enabled',
        examples=[True],
        description=_DESC_ENABLED_CREATE,
    )


class RequestUpdateJob(UpdateJobDomainDTO, APIConfigRequestModel):
    """Request body for partially updating a scheduled job.

    At least one field must be provided. Omitted fields are left unchanged.
    """

    model_config = ConfigDict(
        json_schema_extra={'examples': [_UPDATE_BODY_EXAMPLE]},
    )

    name: Optional[str] = Field(
        None,
        title='Job name',
        examples=['backup_db_updated'],
        description=_DESC_JOB_NAME,
        min_length=1,
        max_length=50,
    )
    description: Optional[str] = Field(
        None,
        title='Description',
        examples=['Incremental backup job'],
        description=_DESC_JOB_DESCRIPTION,
        max_length=255,
    )
    cron_schedule: Optional[str] = Field(
        None,
        title='Cron schedule',
        examples=['0 2 * * *'],
        description=_DESC_CRON,
    )
    command: Optional[str] = Field(
        None,
        title='Command',
        examples=['backup_incremental.sh'],
        description=_DESC_COMMAND,
    )
    enabled: Optional[bool] = Field(
        None,
        title='Enabled',
        examples=[False],
        description=_DESC_ENABLED_UPDATE,
    )


class CreateJobRequest(RequestCreateJob):
    """RDE contract alias for :class:`RequestCreateJob`."""


class UpdateJobRequest(RequestUpdateJob):
    """RDE contract alias for :class:`RequestUpdateJob`."""
