"""Internal DTO models for scheduler domain and service layers."""

from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import Field, field_validator

from openvair.modules.scheduler.config import validate_command
from openvair.common.base_pydantic_models import BaseDTOModel
from openvair.modules.scheduler.shared.validation import (
    validate_cron_schedule,
    validate_optional_name,
    validate_non_empty_name,
    validate_optional_cron_schedule,
)


class CreateJobDomainDTO(BaseDTOModel):
    """Payload for creating a scheduler job (domain/service validation)."""

    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    cron_schedule: str
    command: str = Field(min_length=1)
    enabled: bool = True

    @field_validator('command', mode='before')
    @classmethod
    def validate_cmd(cls, value: str) -> str:
        """Validate command safety and syntax."""
        return validate_command(value)

    @field_validator('cron_schedule', mode='before')
    @classmethod
    def validate_cron(cls, value: str) -> str:
        """Validate cron expression."""
        return validate_cron_schedule(value)

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate job name."""
        return validate_non_empty_name(value)


class UpdateJobDomainDTO(BaseDTOModel):
    """Partial payload for updating a scheduler job."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    cron_schedule: Optional[str] = None
    command: Optional[str] = None
    enabled: Optional[bool] = None

    @field_validator('command', mode='before')
    @classmethod
    def validate_cmd(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional command field."""
        if value is None:
            return value
        return validate_command(value)

    @field_validator('cron_schedule', mode='before')
    @classmethod
    def validate_cron(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional cron expression."""
        return validate_optional_cron_schedule(value)

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional job name."""
        return validate_optional_name(value)


class JobDomainDTO(BaseDTOModel):
    """Scheduler job details used inside the domain layer."""

    id: UUID
    name: str
    cron_schedule: str
    command: str
    enabled: bool
    created_at: datetime
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class JobCreatedDomainDTO(BaseDTOModel):
    """Result of job creation in the domain layer."""

    job_id: UUID


class ApiSchedulerJobDTO(BaseDTOModel):
    """Scheduler job representation for API / service-layer responses."""

    id: UUID
    name: str
    cron_schedule: str
    command: str
    enabled: bool
    created_at: datetime
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class DomainSchedulerJobPayloadDTO(BaseDTOModel):
    """Subset of job fields passed to the domain layer over RPC."""

    id: UUID
    name: str
    cron_schedule: str
    command: str
    enabled: bool
    description: Optional[str] = None


class CreateSchedulerJobOrmDTO(BaseDTOModel):
    """Fields required to persist a new scheduler job."""

    name: str
    cron_schedule: str
    command: str
    enabled: bool = True
    description: Optional[str] = None

