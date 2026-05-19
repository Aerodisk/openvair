"""DTOs for internal service-layer command operations.

This module provides command objects used to describe service and domain-level
operations on schedulers`s jobs (create, edit, delete).
"""
from uuid import UUID
from typing import Optional

from openvair.common.base_pydantic_models import BaseDTOModel


class GetJobServiceCommandDTO(BaseDTOModel):
    """DTO for retrieving a job by its ID.

    Attributes:
        id (UUID): Unique identifier of the job.
    """

    id: UUID


class CreateJobServiceCommandDTO(BaseDTOModel):
    """DTO for creating a job at the service layer.

    Contains metadata required to register a new job in the system.

    Attributes:
        name (str): Unique name of the job.
        description (Optional[str]): Description of the job.
        cron_schedule (str): CRON expression defining job schedule.
        command (str): Command to execute.
        enabled (bool): Indicates whether the job is active.
        before_job_id (Optional[UUID]): Job that must finish before
        this one starts.
        after_job_id (Optional[UUID]): Job that should run after
        this one completes.
    """

    name: str
    description: Optional[str]
    cron_schedule: str
    command: str
    enabled: bool
    before_job_id: UUID
    after_job_id: UUID


class UpdateJobServiceCommandDTO(BaseDTOModel):
    """DTO for updating job fields at the service layer.

    Attributes:
        name (Optional[str]): Updated name for the job.
        description (Optional[str]): Updated description.
        cron_schedule (Optional[str]): Updated CRON schedule.
        command (Optional[str]): Updated command.
        enabled (Optional[bool]): Indicates if the job should be active.
        before_job_id (Optional[UUID]): Updated dependency before another job.
        after_job_id (Optional[UUID]): Updated dependency after another job.
    """

    name: Optional[str]
    description: Optional[str]
    cron_schedule: Optional[str]
    command: Optional[str]
    enabled: Optional[bool]
    before_job_id: Optional[UUID]
    after_job_id: Optional[UUID]


class DeleteJobServiceCommandDTO(BaseDTOModel):
    """DTO for deleting a job at the service layer.

    Attributes:
        id (UUID): ID of the job to delete.
    """

    id: UUID
