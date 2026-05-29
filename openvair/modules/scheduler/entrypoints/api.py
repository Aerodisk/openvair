"""Scheduler API endpoints.

This module exposes HTTP API endpoints for managing schedulers.
It includes operations for listing, retrieving, creating, updating, and deleting
schedulers.

All endpoints require user authentication and rely on the SchedulerCrud adapter
for business logic.

Endpoints:
    - GET /scheduler/jobs - getting a list of all jobs with pagination
    - GET /scheduler/jobs/{job_id} - getting a specific job by ID
    - POST /scheduler/jobs - creating a new scheduler job
    - PATCH /scheduler/jobs/{job_id} - changing job parameters
    - DELETE /scheduler/jobs/{job_id} - deleting a scheduler job

Dependencies:
    - get_current_user: Ensures request is authenticated
    - SchedulerCrud: RPC adapter between API and service layer
"""

from uuid import UUID
from typing import Any, List

from fastapi import Depends, APIRouter, status
from fastapi_pagination import Page, Params, paginate
from starlette.concurrency import run_in_threadpool
from fastapi_pagination.utils import disable_installed_extensions_check

# In-memory pagination after RPC; SQLAlchemy paginate extension does not apply.
disable_installed_extensions_check()

from openvair.libs.log import get_logger
from openvair.common.schemas import BaseResponse
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.scheduler.entrypoints.crud import SchedulerCRUD
from openvair.modules.scheduler.entrypoints.schemas import requests as schemas
from openvair.modules.scheduler.entrypoints.schemas.responses import (
    JobResponse,
    ErrorResponse,
)

LOG = get_logger(__name__)
ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {'model': ErrorResponse, 'description': 'Bad Request'},
    404: {'model': ErrorResponse, 'description': 'Job not found'},
    409: {'model': ErrorResponse, 'description': 'Conflict'},
    422: {'model': ErrorResponse, 'description': 'Validation error'},
    500: {'model': ErrorResponse, 'description': 'Internal server error'},
}

router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
    dependencies=[
        Depends(get_current_user)
    ],  # Глобальная авторизация для всех эндпоинтов
    responses=ERROR_RESPONSES,
)


@router.get(
    '/jobs',
    response_model=BaseResponse[Page[JobResponse]],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def get_jobs(
    crud: SchedulerCRUD = Depends(SchedulerCRUD),
    params: Params = Depends(),
) -> BaseResponse[Page[JobResponse]]:
    """Retrieve a paginated list of all scheduled jobs.

    Returns:
        BaseResponse[Page[JobResponse]]: Paginated response containing jobs.
    """
    LOG.info('Api handle request on getting jobs')

    jobs: List[JobResponse] = await run_in_threadpool(
        crud.get_jobs
    )
    paginated_jobs = paginate(jobs, params)

    LOG.info('Api request on getting jobs was successfully processed')
    return BaseResponse(status='success', data=paginated_jobs)


@router.get(
    '/jobs/{job_id}',
    response_model=BaseResponse[JobResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def get_job(
    job_id: UUID,
    crud: SchedulerCRUD = Depends(SchedulerCRUD),
) -> BaseResponse[JobResponse]:
    """Retrieve details of a specific scheduled job by its ID.

    Returns:
        BaseResponse[JobResponse]: The retrieved job data.
    """
    LOG.info(f'Api handle request on getting job: {job_id}')

    job = await run_in_threadpool(crud.get_job, job_id)

    LOG.info(
        f'Api request on getting job {job_id} '
        'was successfully processed'
    )
    return BaseResponse(status='success', data=job)


@router.post(
    '/jobs',
    response_model=BaseResponse[JobResponse],
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
async def create_job(
    data: schemas.CreateJobRequest,
    crud: SchedulerCRUD = Depends(SchedulerCRUD),
) -> BaseResponse:
    """Create a new scheduled job and sync it with the OS crontab.

    Returns:
        BaseResponse[JobResponse]: The newly created job data.
    """
    LOG.info('Api handle request on creating job')

    job = await run_in_threadpool(crud.create_job, data)

    LOG.info('Api request on creating job was successfully processed')
    return BaseResponse(status='success', data=job)


@router.patch(
    '/jobs/{job_id}',
    response_model=BaseResponse[JobResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def update_job(
    job_id: UUID,
    data: schemas.UpdateJobRequest,
    crud: SchedulerCRUD = Depends(SchedulerCRUD),
) -> BaseResponse:
    """Update an existing scheduled job's parameters.

    Returns:
        BaseResponse[JobResponse]: The updated job data.
    """
    LOG.info(f'Api handle request on editing job {job_id}')

    job = await run_in_threadpool(crud.update_job, job_id, data)

    LOG.info(
        f'Api request on editing job {job_id} '
        'was successfully processed'
    )
    return BaseResponse(status='success', data=job)


@router.delete(
    '/jobs/{job_id}',
    response_model=BaseResponse[JobResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
async def delete_job(
    job_id: UUID,
    crud: SchedulerCRUD = Depends(SchedulerCRUD),
) -> BaseResponse:
    """Delete a scheduled job from the database and OS crontab by its ID.

    Returns:
        BaseResponse[JobResponse]: Data of the deleted job.
    """
    LOG.info(f'Api handle request on deleting job {job_id}')

    job = await run_in_threadpool(crud.delete_job, job_id)

    LOG.info(
        f'Api request on deleting job {job_id} '
        'was successfully processed'
    )
    return BaseResponse(status='success', data=job)
