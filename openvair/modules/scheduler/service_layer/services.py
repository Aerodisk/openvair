"""Scheduler service basic operations (get, create, edit, delete)."""

from typing import TYPE_CHECKING, Any, Dict, List, Type

from croniter import croniter

from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.modules.scheduler.adapters.serializer import (
    SchedulerJobSerializer,
)
from openvair.modules.scheduler.service_layer.exceptions import (
    JobNotFoundError,
    JobInvalidNameError,
    JobNameAlreadyExists,
    JobFieldIsNotEditable,
    JobInvalidCronExpression,
)

if TYPE_CHECKING:
    from openvair.modules.scheduler.service_layer.unit_of_work import (
        SchedulerSqlAlchemyUnitOfWork,
    )


class SchedulerService:
    """Service layer for managing scheduler jobs."""

    def __init__(self, uow: Type['SchedulerSqlAlchemyUnitOfWork']) -> None:
        """Initialize scheduler service with unit of work."""
        self.uow = uow

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Retrieve all scheduler jobs."""
        with self.uow() as u:
            return [
                SchedulerJobSerializer.to_web(job) for job in u.jobs.get_all()
            ]

    def create_job(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scheduler job."""
        if not isinstance(data.get('name'), str) or not data['name'].strip():
            message = 'Job name cannot be empty'
            raise JobInvalidNameError(message)

        cron_schedule = data.get('cron_schedule')
        if not isinstance(cron_schedule, str) or not croniter.is_valid(
            cron_schedule
        ):
            message = 'Invalid cron expression'
            raise JobInvalidCronExpression(message)

        with self.uow() as u:
            if u.jobs.get_by_name(data['name']):
                message = 'Job already exists'
                raise JobNameAlreadyExists(message)

            new_job = SchedulerJobSerializer.to_db(data)
            u.jobs.add(new_job)
            return SchedulerJobSerializer.to_web(new_job)

    def edit_job(self, job_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Edit an existing scheduler job."""
        with self.uow() as u:
            job = self._get_job_or_raise(u, job_id)
            allowed_fields = self._validate_edit_data(u, job, data)

            for key in allowed_fields & data.keys():
                setattr(job, key, data[key])

            return SchedulerJobSerializer.to_web(job)

    def delete_job(self, job_id: int) -> Dict[str, Any]:
        """Delete scheduler job by its ID."""
        with self.uow() as u:
            job = u.jobs.get_by_id(job_id)

            if not job:
                message = 'Job id does not exist'
                raise JobNotFoundError(message)

            u.jobs.delete(job)
            return SchedulerJobSerializer.to_web(job)

    def _get_job_or_raise(
        self, u: 'SchedulerSqlAlchemyUnitOfWork', job_id: int
    ) -> SchedulerJob:
        """Retrieve job by id or raise not found error."""
        job = u.jobs.get_by_id(job_id)
        if not job:
            message = 'Job id does not exist'
            raise JobNotFoundError(message)
        return job

    def _validate_edit_data(
        self,
        u: 'SchedulerSqlAlchemyUnitOfWork',
        job: SchedulerJob,
        data: Dict[str, Any],
    ) -> set[str]:
        """Validate editable data before applying changes."""
        cron_schedule = data.get('cron_schedule')
        if (
            cron_schedule
            and isinstance(cron_schedule, str)
            and not croniter.is_valid(cron_schedule)
        ):
            message = 'Invalid cron expression'
            raise JobInvalidCronExpression(message)

        existing = u.jobs.get_by_name(data['name'])
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
            message = (
                'Field(s) '
                f'{invalid} are not editable or do not exist.'
            )
            raise JobFieldIsNotEditable(message)

        return allowed_fields
