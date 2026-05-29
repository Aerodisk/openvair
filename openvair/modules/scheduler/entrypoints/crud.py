"""CRUD adapter for the scheduler HTTP API.

Mediates between API handlers and the service layer using RPC calls.
"""

from uuid import UUID
from typing import Any, Dict, List

from fastapi import HTTPException, status

from openvair.libs.log import get_logger
from openvair.modules.scheduler.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.scheduler.service_layer.services import (
    SchedulerServiceLayerManager,
)
from openvair.modules.scheduler.entrypoints.schemas.requests import (
    CreateJobRequest,
    UpdateJobRequest,
)
from openvair.modules.scheduler.entrypoints.schemas.responses import (
    JobResponse,
)
from openvair.modules.scheduler.adapters.dto.internal.commands import (
    GetJobServiceCommandDTO,
    CreateJobServiceCommandDTO,
    DeleteJobServiceCommandDTO,
    UpdateJobServiceCommandDTO,
)

LOG = get_logger(__name__)


def _translate_rpc_exception(error: Exception) -> HTTPException:
    """Map service/domain errors to API-level HTTP exceptions."""
    message = str(error)
    lower = message.lower()

    if 'not found' in lower or 'does not exist' in lower:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
    if 'already exists' in lower:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )
    if (
        'invalid' in lower
        or 'cannot delete enabled job' in lower
        or 'dependency' in lower
        or 'maximum number of active jobs' in lower
    ):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Internal scheduler error',
    )


class SchedulerCRUD:
    """RPC-based access to scheduler service-layer operations."""

    def __init__(self) -> None:
        """Initialize the RPC client for the scheduler service layer."""
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_jobs(self) -> List[JobResponse]:
        """Retrieve a list of all jobs via RPC."""
        LOG.info('Call service layer on getting jobs.')

        try:
            result: List[Dict[str, Any]] = self.service_layer_rpc.call(
                SchedulerServiceLayerManager.get_all_jobs.__name__,
                data_for_method={},
            )
        except Exception as error:
            raise _translate_rpc_exception(error) from error

        return [JobResponse.model_validate(item) for item in result]

    def get_jobs(self) -> List[JobResponse]:
        """Compatibility method name for API contracts."""
        return self.get_all_jobs()

    def get_job(self, job_id: UUID) -> JobResponse:
        """Retrieve a specific job by its ID via RPC."""
        LOG.info(f'Call service layer on getting job {job_id}.')

        getting_command_dto = GetJobServiceCommandDTO(id=job_id)
        try:
            result: Dict[str, Any] = self.service_layer_rpc.call(
                SchedulerServiceLayerManager.get_job.__name__,
                data_for_method=getting_command_dto.model_dump(mode='json'),
            )
        except Exception as error:
            raise _translate_rpc_exception(error) from error

        return JobResponse.model_validate(result)

    def create_job(
        self, creation_data: CreateJobRequest
    ) -> JobResponse:
        """Create a new job using provided data via RPC."""
        LOG.info('Call service layer on creating new job.')

        creation_command = CreateJobServiceCommandDTO.model_validate(
            creation_data
        )
        try:
            result: Dict[str, Any] = self.service_layer_rpc.call(
                SchedulerServiceLayerManager.create_job.__name__,
                data_for_method=creation_command.model_dump(mode='json'),
            )
        except Exception as error:
            raise _translate_rpc_exception(error) from error

        return JobResponse.model_validate(result)

    def edit_job(
        self,
        job_id: UUID,
        edit_data: UpdateJobRequest,
    ) -> JobResponse:
        """Update an existing job using partial data via RPC."""
        LOG.info(f'Call service layer on editing job {job_id}.')

        editing_command = UpdateJobServiceCommandDTO(
            id=job_id,
            **edit_data.model_dump(exclude_none=True),
        )
        try:
            result: Dict[str, Any] = self.service_layer_rpc.call(
                SchedulerServiceLayerManager.edit_job.__name__,
                data_for_method=editing_command.model_dump(
                    mode='json',
                    exclude_none=True,
                ),
            )
        except Exception as error:
            raise _translate_rpc_exception(error) from error
        return JobResponse.model_validate(result)

    def update_job(
        self,
        job_id: UUID,
        edit_data: UpdateJobRequest,
    ) -> JobResponse:
        """Compatibility method name for API contracts."""
        return self.edit_job(job_id, edit_data)

    def delete_job(self, job_id: UUID) -> JobResponse:
        """Delete a job by its ID via RPC."""
        LOG.info(f'Call service layer on deleting job {job_id}.')

        deleting_command = DeleteJobServiceCommandDTO(id=job_id)
        try:
            result: Dict[str, Any] = self.service_layer_rpc.call(
                SchedulerServiceLayerManager.delete_job.__name__,
                data_for_method=deleting_command.model_dump(mode='json'),
            )
        except Exception as error:
            raise _translate_rpc_exception(error) from error
        return JobResponse.model_validate(result)


class SchedulerCrud(SchedulerCRUD):
    """Backward-compatible class name kept for existing imports/tests."""
