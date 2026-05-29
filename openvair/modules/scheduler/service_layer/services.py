"""Scheduler service basic operations (get, create, edit, delete)."""

import datetime
from uuid import UUID
from typing import Any, Set, Dict, List
from contextlib import suppress

from pydantic import ValidationError

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks, periodic_task
from openvair.modules.scheduler.config import (
    MAX_CONCURRENT_JOBS,
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
    domain_scheduler_manager_data,
)
from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.scheduler.shared.validation import (
    validate_optional_cron_schedule,
)
from openvair.modules.scheduler.adapters.serializer import (
    SchedulerJobSerializer,
)
from openvair.modules.scheduler.service_layer.exceptions import (
    JobNotFoundError,
    JobDependencyError,
    JobInvalidNameError,
    JobNameAlreadyExists,
    JobFieldIsNotEditable,
    JobInvalidCronExpression,
)
from openvair.modules.scheduler.service_layer.unit_of_work import (
    SchedulerSqlAlchemyUnitOfWork,
)
from openvair.modules.scheduler.adapters.dto.internal.commands import (
    CreateJobServiceCommandDTO,
)

JOB_LIFETIME_THRESHOLD_SECS = 30

LOG = get_logger(__name__)


class SchedulerServiceLayerManager(BackgroundTasks):
    """Manager for coordinating scheduler operations in the service layer.

    This class orchestrates scheduler-related tasks such as creation,
    updating, and deletion. It handles RPC communication, database transactions,
    domain delegation, and event logging.

    Attributes:
        uow (SchedulerSqlAlchemyUnitOfWork): Unit of Work for scheduler
            transactions.
        domain_rpc (MessagingClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (MessagingClient): RPC client for internal task
            delegation.
    """

    def __init__(self) -> None:
        """Initialize the SchedulerServiceLayerManager.

        Sets up messaging clients, unit of work, and RPC clients.
        """
        super().__init__()
        self.uow = SchedulerSqlAlchemyUnitOfWork
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Retrieve all scheduler jobs."""
        with self.uow() as uow:
            orm_jobs = uow.jobs.get_all()

        api_jobs: List[Dict[str, Any]] = [
            SchedulerJobSerializer.to_web(job) for job in orm_jobs
        ]

        LOG.info(
            'Service layer request on getting jobs was successfully processed'
        )

        return api_jobs

    def create_job(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scheduler job."""
        try:
            validated = CreateJobServiceCommandDTO.model_validate(data)
        except ValidationError as error:
            message = str(error)
            if 'cron' in message.lower():
                raise JobInvalidCronExpression(message) from error
            raise JobInvalidNameError(message) from error

        data = validated.model_dump()

        with self.uow() as uow:
            active_jobs = [job for job in uow.jobs.get_all() if job.enabled]
            if (
                data.get('enabled', True)
                and len(active_jobs) >= MAX_CONCURRENT_JOBS
            ):
                message = (
                    f'Maximum number of active jobs reached: '
                    f'{MAX_CONCURRENT_JOBS}'
                )
                raise JobInvalidNameError(message)

            if uow.jobs.get_by_name(data['name']):
                message = 'Job with that name already exists'
                raise JobNameAlreadyExists(message)

            new_job = SchedulerJobSerializer.to_db(data)
            uow.jobs.add(new_job)

            uow.commit()
            uow.session.refresh(new_job)

            LOG.info('Casting to domain layer to create a job')
            domain_payload = SchedulerJobSerializer.to_domain(new_job)

            self.domain_rpc.call(
                method_name='create',
                data_for_manager=domain_scheduler_manager_data(),
                data_for_method=domain_payload
            )

            return SchedulerJobSerializer.to_web(new_job)

    def edit_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Edit an existing scheduler job."""
        job_id = payload['id']
        data = {k: v for k, v in payload.items() if k != 'id'}

        with self.uow() as uow:
            job = self._retrieve_job(uow, job_id)
            allowed_fields = self._validate_edit_data(uow, job, data)

            for key in allowed_fields & data.keys():
                setattr(job, key, data[key])

            uow.commit()
            uow.session.refresh(job)

            LOG.info('Casting to domain layer to edit a job')
            domain_payload = SchedulerJobSerializer.to_domain(job)

            self.domain_rpc.call(
                method_name='edit',
                data_for_manager=domain_scheduler_manager_data(),
                data_for_method=domain_payload
            )

            return SchedulerJobSerializer.to_web(job)

    def _retrieve_job(
        self, u: 'SchedulerSqlAlchemyUnitOfWork', job_id: UUID
    ) -> SchedulerJob:
        """Retrieve job by id or raise not found error."""
        job = u.jobs.get_by_id(job_id)
        if not job:
            message = 'Job id does not exist'
            raise JobNotFoundError(message)
        return job

    def _validate_edit_data(  # noqa: C901
        self,
        u: 'SchedulerSqlAlchemyUnitOfWork',
        job: SchedulerJob,
        data: Dict[str, Any],
    ) -> Set[str]:
        """Validate editable data before applying changes."""
        cron_schedule = data.get('cron_schedule')
        if cron_schedule is not None:
            try:
                validate_optional_cron_schedule(cron_schedule)
            except ValueError as error:
                raise JobInvalidCronExpression(str(error)) from error

        new_name = data.get('name')
        if new_name is not None:
            existing = u.jobs.get_by_name(new_name)
            if existing and existing.id != job.id:
                message = 'Job already exists'
                raise JobNameAlreadyExists(message)

        allowed_fields = {
            'name',
            'description',
            'cron_schedule',
            'command',
            'enabled',
        }

        invalid_fields = set(data) - allowed_fields
        if invalid_fields:
            invalid = ', '.join(sorted(invalid_fields))
            message = f'Field(s) {invalid} are not editable or do not exist.'
            raise JobFieldIsNotEditable(message)

        if data.get('enabled') is True and not job.enabled:
            active_jobs = [item for item in u.jobs.get_all() if item.enabled]
            if len(active_jobs) >= MAX_CONCURRENT_JOBS:
                message = (
                    f'Maximum number of active jobs reached: '
                    f'{MAX_CONCURRENT_JOBS}'
                )
                raise JobFieldIsNotEditable(message)

        return allowed_fields

    def delete_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete scheduler job by its ID."""
        job_id = payload['id']

        with self.uow() as uow:
            job = uow.jobs.get_by_id(job_id)

            if not job:
                message = 'Job id does not exist'
                raise JobNotFoundError(message)

            if job.enabled:
                message = (
                    'Cannot delete enabled job. '
                    'Disable job first to satisfy dependency checks.'
                )
                raise JobDependencyError(message)

            uow.jobs.delete(job)
            uow.commit()

            self.domain_rpc.call(
                method_name='delete',
                data_for_manager=domain_scheduler_manager_data(),
                data_for_method={'job_id': str(job_id)}
            )

            return SchedulerJobSerializer.to_web(job)

    def get_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get scheduler job by its UUID."""
        job_id = payload['id']

        with self.uow() as uow:
            job = self._retrieve_job(uow, job_id)

            return SchedulerJobSerializer.to_web(job)


    @periodic_task(interval=10)
    def monitoring(self) -> None: #noqa: C901
        """Monitor and synchronize scheduled jobs with the system crontab.

        This periodic task fetches all OpenVair jobs from the OS crontab and
        synchronizes their runtimes (last_run, next_run) and enabled state
        with the database. It also handles orphaned or missing jobs.
        """
        LOG.info('Start monitoring scheduler jobs')

        # 1. Gather jobs from OS crontab
        try:
            domain_response: Dict[str, Any] = self.domain_rpc.call(
                method_name='list_all',
                data_for_manager=domain_scheduler_manager_data(),
                data_for_method={}
            )
            os_jobs = domain_response.get('jobs', [])
            os_jobs_map = {str(job['id']): job for job in os_jobs}
        except Exception as error: # noqa: BLE001
            LOG.error(f"Monitoring failed to fetch jobs from OS: {error}")
            return
        with self.uow() as uow:
            db_jobs = uow.jobs.get_all()

            # 2. Get all jobs in service layer's db
            for db_job in db_jobs:
                job_id_str = str(db_job.id)
                os_job_data = os_jobs_map.get(job_id_str)

                if os_job_data:
                    # If job is presented both in db and in OS crontab
                    #   Synchronise execution dates and status (enabled or not)
                    self.__synchronize_os_to_db_info(db_job, os_job_data)
                    # Remove correct job from stack,
                    # so it only contains jobs with errors
                    os_jobs_map.pop(job_id_str)
                else:
                    # Job is presented in DB but not in OS crontab
                    # Race condition guard: check that job was not JUST created
                    current_time = datetime.datetime.now()
                    job_created_at = db_job.created_at
                    job_age = (current_time - job_created_at).total_seconds()
                    if (
                        db_job.enabled
                        and job_age > JOB_LIFETIME_THRESHOLD_SECS
                    ):
                        LOG.warning(
                            f"Job {job_id_str} not found in OS crontab. "
                            f"Disabling in database."
                        )
                        db_job.enabled = False

            # 3. Delete jobs in OS that are not presented in service layer's DB
            for orphan_id in os_jobs_map:
                msg = f"Found orphaned job {orphan_id} in OS. Deleting."
                LOG.warning(msg)
                try:
                    self.domain_rpc.call(
                        method_name='delete',
                        data_for_manager=domain_scheduler_manager_data(),
                        data_for_method={
                            'job_id': orphan_id
                        }
                    )
                except Exception as error: # noqa: BLE001
                    msg = f"Failed to delete orphaned job {orphan_id}: {error}"
                    LOG.error(msg)

            uow.commit()

        LOG.info('Stop monitoring scheduler jobs')

    def __synchronize_os_to_db_info(
        self, db_job: SchedulerJob, os_job_data: Dict[str, Any]
    ) -> None:
        """Update DB job attributes based on OS job data (runs and status)."""
        # Synchronize scheduler_jobs.last_run
        last_run_str = os_job_data.get('last_run')
        if last_run_str:
            with suppress(ValueError):
                datetime_iso = datetime.datetime.fromisoformat(last_run_str)
                db_job.last_run = datetime_iso.replace(tzinfo=None)

        # Synchronize scheduler_jobs.next_run
        next_run_str = os_job_data.get('next_run')
        if next_run_str:
            with suppress(ValueError):
                datetime_iso = datetime.datetime.fromisoformat(next_run_str)
                db_job.next_run = datetime_iso.replace(tzinfo=None)

        # Synchronize scheduler_jobs.enabled
        os_enabled = os_job_data.get('enabled')
        if os_enabled is not None and db_job.enabled != os_enabled:
            LOG.info(
                f"Syncing enabled state for job {db_job.id}: "
                f"DB({db_job.enabled}) -> OS({os_enabled})"
            )
            db_job.enabled = os_enabled


class SchedulerService(SchedulerServiceLayerManager):
    """Compatibility alias for requirements naming."""

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Retrieve all scheduler jobs."""
        return super().get_all_jobs()

    def create_job(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a scheduler job."""
        return super().create_job(data)

    def edit_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Edit scheduler job payload."""
        return super().edit_job(payload)

    def delete_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete scheduler job payload."""
        return super().delete_job(payload)
