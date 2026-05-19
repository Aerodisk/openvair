"""CRUD adapter for Template API.

This module defines the SchedulerCrud class, which mediates between API handlers
and the service layer using RPC calls.

The methods of this class are responsible for invoking service-layer logic
using strongly typed DTOs and returning validated response models.

Classes:
    - SchedulerCrud: Encapsulates all scheduler-related RPC logic.

Dependencies:
    - MessagingClient: Generic RPC client for service-to-service communication.
    - TemplateServiceLayerManager: RPC method names for the service layer.
"""

from uuid import UUID
from typing import Any, Dict, List

from openvair.libs.log import get_logger
from openvair.modules.template.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.scheduler.entrypoints.schemas.requests import (
    RequestCreateJob,
    RequestUpdateJob,
)
from openvair.modules.scheduler.entrypoints.schemas.responses import (
    JobResponse,
    JobListResponse,
)
from openvair.modules.scheduler.adapters.dto.internal.commands import (
    GetJobServiceCommandDTO,
    CreateJobServiceCommandDTO,
    DeleteJobServiceCommandDTO,
    UpdateJobServiceCommandDTO,
)

LOG = get_logger(__name__)


class SchedulerCrud:
    """Provides RPC-based access to scheduler service operations.

    This class encapsulates all logic required by the API layer to interact
    with the service layer for scheduler and volume management.

    Attributes:
        service_layer_rpc (MessagingClient): RPC client for calling service
            methods.
    """

    def __init__(self) -> None:
        """Initialize the SchedulerCrud instance.

        Sets up the RPC client for the template service layer.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_jobs(self) -> List[JobListResponse]:
        """Retrieve a list of all jobs via RPC.

        Returns:
            List[JobListResponse]: A list of all available jobs.
        """
        LOG.info('Call service layer on getting jobs.')

        result: List[Dict[str, Any]] = self.service_layer_rpc.call(
            SchedulerServiceLayerManager.get_all_jobs.__name__,
            data_for_method={},
        )

        return [JobListResponse.model_validate(item) for item in result]

    def get_job(self, job_id: UUID) -> JobResponse:
        """Retrieve a specific job by its ID via RPC.

        Args:
            job_id (UUID): The ID of the job to retrieve.

        Returns:
            JobResponse: The retrieved job object.
        """
        LOG.info(f'Call service layer on getting template {job_id}.')

        getting_command_dto = GetJobServiceCommandDTO(id=job_id)
        result: Dict[str, Any] = self.service_layer_rpc.call(
            SchedulerServiceLayerManager.get_job.__name__,
            data_for_method=getting_command_dto.model_dump(mode='json'),
        )

        return JobResponse.model_validate(result)

    def create_job(
        self, creation_data: RequestCreateJob
    ) -> JobResponse:
        """Create a new job using provided data via RPC.

        Args:
            creation_data (RequestCreateJob): The job creation data.

        Returns:
            JobResponse: The created job object.
        """
        LOG.info('Call service layer on creating new job.')

        creation_command = CreateJobServiceCommandDTO.model_validate(
            creation_data
        )
        result: Dict[str, Any] = self.service_layer_rpc.call(
            SchedulerServiceLayerManager.create_job.__name__,
            data_for_method=creation_command.model_dump(mode='json'),
        )

        return JobResponse.model_validate(result)

    def edit_job(
        self,
        job_id: UUID,
        edit_data: RequestUpdateJob,
    ) -> JobResponse:
        """Update an existing job using partial data via RPC.

        Args:
            job_id (UUID): The ID of the job to update.
            edit_data (BaseModel): The updated fields for the job.

        Returns:
            JobResponse: The updated job object.
        """
        LOG.info(f'Call service layer on editing job {job_id}.')

        editing_command = UpdateJobServiceCommandDTO(
            **edit_data.model_dump(exclude_none=True)
        )
        result: Dict[str, Any] = self.service_layer_rpc.call(
            SchedulerServiceLayerManager.edit_job.__name__,
            data_for_method=editing_command.model_dump(mode='json'),
        )
        return JobResponse.model_validate(result)

    def delete_job(self, job_id: UUID) -> JobResponse:
        """Delete a job by its ID via RPC.

        Args:
            job_id (UUID): The ID of the job to delete.

        Returns:
            JobResponse: The deleted job object.
        """
        LOG.info(f'Call service layer on deleting job {job_id}.')

        deleting_command = DeleteJobServiceCommandDTO(id=job_id)
        result: Dict[str, Any] = self.service_layer_rpc.call(
            SchedulerServiceLayerManager.delete_job.__name__,
            data_for_method=deleting_command.model_dump(mode='json'),
        )
        return JobResponse.model_validate(result)
