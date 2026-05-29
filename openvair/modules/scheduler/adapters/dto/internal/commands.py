"""DTOs for internal service-layer command operations.

This module provides command objects used to describe service and domain-level
operations on schedulers`s jobs (create, edit, delete).
"""
from uuid import UUID

from openvair.common.base_pydantic_models import BaseDTOModel
from openvair.modules.scheduler.adapters.dto.internal.models import (
    CreateJobDomainDTO,
    UpdateJobDomainDTO,
)


class GetJobServiceCommandDTO(BaseDTOModel):
    """DTO for retrieving a job by its ID.

    Attributes:
        id (UUID): Unique identifier of the job.
    """

    id: UUID


class CreateJobServiceCommandDTO(CreateJobDomainDTO):
    """DTO for creating a job at the service layer."""


class UpdateJobServiceCommandDTO(UpdateJobDomainDTO):
    """DTO for updating job fields at the service layer."""

    id: UUID


class DeleteJobServiceCommandDTO(BaseDTOModel):
    """DTO for deleting a job at the service layer.

    Attributes:
        id (UUID): ID of the job to delete.
    """

    id: UUID
