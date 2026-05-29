"""Response models for scheduler API endpoints.

Defines schemas used to serialize and return job data from the scheduler API.

Classes:
    - JobResponse
    - JobListResponse
    - JobCreateResponse
    - JobDeleteResponse
    - ErrorResponse
"""

from uuid import UUID
from typing import List, Optional
from datetime import datetime

from pydantic import Field

from openvair.common.base_pydantic_models import APIConfigResponseModel


class JobResponse(APIConfigResponseModel):
    """Schema representing a single scheduled job in API responses.

    Attributes:
        id (UUID): Unique identifier of the job.
        name (str): Name of the scheduled job.
        description (Optional[str]): Job description.
        cron_schedule (str): CRON expression defining job schedule.
        command (str): Command executed by the job.
        enabled (bool): Indicates whether the job is active.
        created_at (datetime): Timestamp when the job was created.
        updated_at (datetime): Timestamp when the job was last updated.
        last_run (Optional[datetime]): Timestamp of the last job run.
        next_run (Optional[datetime]): Timestamp of the next scheduled run.
    """

    id: UUID = Field(
        ...,
        examples=["a73f920b-d282-41e4-8ec1-6e6b89d3a9e7"],
        description="Unique identifier of the job",
    )
    name: str = Field(
        ...,
        examples=["backup_daily"],
        description="Name of the scheduled job",
    )
    description: Optional[str] = Field(
        None,
        examples=["Daily backup job for database"],
        description="Description of the scheduled job",
    )
    cron_schedule: str = Field(
        ...,
        examples=["0 3 * * *"],
        description="CRON expression defining when the job runs",
    )
    command: str = Field(
        ...,
        examples=["backup.sh"],
        description="Command executed when the job runs",
    )
    enabled: bool = Field(
        ...,
        examples=[True],
        description="Indicates whether the job is enabled",
    )
    created_at: datetime = Field(
        ...,
        examples=["2024-05-28T10:45:21.000Z"],
        description="Timestamp when the job was created",
    )
    updated_at: Optional[datetime] = Field(
        ...,
        examples=["2024-06-01T09:12:45.000Z"],
        description="Timestamp when the job was last updated",
    )
    last_run: Optional[datetime] = Field(
        None,
        examples=["2024-06-02T03:00:00.000Z"],
        description="Timestamp of the last job run",
    )
    next_run: Optional[datetime] = Field(
        None,
        examples=["2024-06-03T03:00:00.000Z"],
        description="Timestamp of the next scheduled job run",
    )


class JobListResponse(APIConfigResponseModel):
    """Schema representing a paginated list of scheduled jobs."""

    total: int = Field(
        ...,
        examples=[42],
        description="Total number of jobs in the system",
    )
    items: List[JobResponse] = Field(
        ...,
        description="List of job entries for the current page",
    )


class JobCreateResponse(APIConfigResponseModel):
    """Schema returned after successfully creating a new job."""

    job_id: UUID = Field(
        ...,
        examples=["e8d321b7-1a34-4a12-91cf-7dbbf017e8a3"],
        description="Unique identifier of the created job",
    )
    message: str = Field(
        default="Job successfully created",
        examples=["Job successfully created"],
        description="Message confirming successful job creation",
    )


class JobDeleteResponse(APIConfigResponseModel):
    """Schema returned after successfully deleting a job."""

    job_id: UUID = Field(
        ...,
        examples=["f2c812b7-9a34-4a12-91cf-7dbbf017e8a3"],
        description="Identifier of the deleted job",
    )
    message: str = Field(
        default="Job deleted successfully",
        examples=["Job deleted successfully"],
        description="Message confirming job deletion",
    )


class ErrorResponse(APIConfigResponseModel):
    """Unified schema for API error responses."""

    error: str = Field(
        ...,
        examples=["Job not found"],
        description="Short error message",
    )
    details: Optional[str] = Field(
        None,
        examples=["Job with the specified ID does not exist"],
        description="Additional details about the error, if provided",
    )


class CreateJobResponse(JobCreateResponse):
    """Backward-compatible alias matching external API contract naming."""


class DeleteResponse(JobDeleteResponse):
    """Backward-compatible alias matching external API contract naming."""


class JobStatusResponse(APIConfigResponseModel):
    """Schema representing job execution/enabled status."""

    job_id: UUID = Field(
        ...,
        examples=["e8d321b7-1a34-4a12-91cf-7dbbf017e8a3"],
        description="Identifier of the scheduler job",
    )
    enabled: bool = Field(
        ...,
        examples=[True],
        description="Current enabled state of the job",
    )
    status: str = Field(
        ...,
        examples=["scheduled"],
        description="Current job status label",
    )
