# mypy: disable-error-code="no-any-unimported, unused-ignore"

"""Cron Job Scheduler

This module defines the `CronJobScheduler` concrete class that allows
management of cron jobs
"""

from __future__ import annotations

import uuid
import datetime
from typing import Any, Dict, Optional

from crontab import CronTab, CronItem  # type: ignore

from openvair.libs.log import get_logger
from openvair.modules.scheduler.domain.base import BaseScheduler
from openvair.modules.scheduler.domain.exception import (
    CronJobNotFound,
)
from openvair.modules.scheduler.shared.base_exceptions import (
    SchedulerDomainException,
)
from openvair.modules.scheduler.adapters.dto.internal.models import (
    JobDomainDTO,
    CreateJobDomainDTO,
    UpdateJobDomainDTO,
    JobCreatedDomainDTO,
)

LOG = get_logger(__name__)


class CronJobScheduler(BaseScheduler):
    """Concrete implementation of BaseScheduler for system cron jobs.

    This class provides specific logic for interacting with the system crontab.
    """

    def __init__(self, cron_obj: Optional[CronTab] = None) -> None:
        """Initialize the CronJobScheduler."""
        super().__init__()
        if cron_obj is not None:
            self._cron = cron_obj
        else:
            self._cron = CronTab(user=True)

    def __create_job(
        self,
        req: CreateJobDomainDTO,
        job_id_str: str,
    ) -> CronItem:
        with self._cron as cron:
            desc = req.description or ''
            custom_comment = f"{desc} OPENVAIR_JOB_ID:[{job_id_str}]".strip()

            job = cron.new(
                command=req.command,
                comment=custom_comment,
            )
            job.setall(req.cron_schedule)
        return job

    def create(self, creation_data: Dict[str, Any]) -> Dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Create a scheduled task and store its metadata.

        Args:
            creation_data (Dict[str, Any]): Dictionary with job creation data.

        Returns:
            Dict[str, Any]: Dictionary containing the new job_id.
        """
        try:
            job_id_str = str(creation_data['id'])
            job_id = uuid.UUID(job_id_str)

            validation_data = creation_data.copy()
            validation_data.pop('id', None)

            req = CreateJobDomainDTO.model_validate(validation_data)

            self.__create_job(req, job_id_str)

            resp = JobCreatedDomainDTO(job_id=job_id)
            return resp.model_dump(mode='json')

        except SchedulerDomainException as error:
            LOG.error(f'Failed to create a scheduled task: {error}')
            raise

    def get(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve job details by ID.

        Args:
            job_id (str): UUID of the job as a string.
            data (Dict[str, Any]): Dictionary with job data from
            service layer enriched by domain layer.

        Returns:
            Dict[str, Any]: Job details including schedule and run times.
        """
        try:
            job_id_str = str(data.get('id'))
            job_uuid = uuid.UUID(job_id_str)

            with self._cron as cron:
                item = self._find_cron_item(job_id_str, cron)
                job_schedule = item.schedule()

                resp = JobDomainDTO(
                    id=job_uuid,
                    name=data.get('name', 'Unknown'),
                    description=item.comment.split(' OPENVAIR')[0].strip(),
                    cron_schedule=str(item.slices),
                    command=item.command, # type: ignore
                    enabled=item.is_enabled(),
                    created_at=data.get('created_at', datetime.datetime.now()),
                    updated_at=data.get('updated_at'),
                    last_run=job_schedule.get_prev(),
                    next_run=job_schedule.get_next(),
                )

            return resp.model_dump(mode='json')
        except SchedulerDomainException as error:
            LOG.error(f'Failed to get scheduled task: {error}')
            raise

    def delete(self, data: Dict[str, Any]) -> None:
        """Delete job by UUID.

        Args:
            data (Dict[str, Any]): Dictionary with job_id.
        """
        try:
            job_id_str = str(data['job_id'])
            target_comment = f"OPENVAIR_JOB_ID:[{job_id_str}]"

            with self._cron as cron:
                for item in cron:
                    if item.comment and target_comment in item.comment:
                        cron.remove(item)

        except (KeyError, OSError) as error:
            msg = f'Failed to delete job {data.get("job_id")}: {error}'
            LOG.error(msg)
            raise SchedulerDomainException(str(error))

    def list_all(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: #noqa: C901
        """Retrieve all scheduled tasks.

        Args:
            data (Dict[str, Any]): Dictionary with request data (can be empty).

        Returns:
            Dict[str, Any]: Dictionary containing the list of jobs.
        """
        if data is None:
            data = {}

        try:
            jobs_list = []

            # Service layer should pass DB objects to construct full responses,
            # but if it doesn't, we return what we can find in OS.
            db_jobs = data.get('jobs_from_db', [])
            db_jobs_map = {str(j.get('id')): j for j in db_jobs}

            with self._cron as cron:
                for item in cron:
                    if item.comment and "OPENVAIR_JOB_ID:[" in item.comment:
                        # Extract UUID from comment
                        # "some desc OPENVAIR_JOB_ID:[uuid-string]"
                        ext = item.comment.split('OPENVAIR_JOB_ID:[')[-1].strip(']') #noqa: E501

                        try:
                            job_uuid = uuid.UUID(ext)
                        except ValueError:
                            continue # Ignore malformed IDs

                        db_info = db_jobs_map.get(ext, {})

                        resp = JobDomainDTO(
                            id=job_uuid,
                            name=db_info.get('name', 'Unknown'),
                            description=item.comment.split(' OPENVAIR')[0].strip(), #noqa: E501
                            cron_schedule=str(item.slices),
                            command=item.command, # type: ignore
                            enabled=item.is_enabled(),
                            created_at=db_info.get('created_at',
                                                   datetime.datetime.now()),
                            updated_at=db_info.get('updated_at'),
                            last_run=item.schedule().get_prev(datetime.datetime),
                            next_run=item.schedule().get_next(datetime.datetime),
                        )
                        jobs_list.append(resp.model_dump(mode='json'))

            return {'jobs': jobs_list} #noqa: TRY300

        except SchedulerDomainException as error:
            LOG.error(f'Failed to get all scheduled tasks: {error}')
            raise

    def _find_cron_item(self, job_id_str: str, cron: CronTab) -> CronItem:
        """Helper to search job in OS crontab by tag in comment"""
        target_tag = f"OPENVAIR_JOB_ID:[{job_id_str}]"
        for item in cron:
            if item.comment and target_tag in item.comment:
                return item
        raise CronJobNotFound(job_id_str)

    def edit(self, editing_data: Dict[str, Any]) -> Dict[str, Any]: #noqa: C901
        """Modify an existing scheduled task."""
        try:
            job_id_str = str(editing_data.get('id'))

            # Remove id from payload because it is only needed for search
            # and not for editing

            validation_data = editing_data.copy()
            validation_data.pop('id', None)

            req = UpdateJobDomainDTO.model_validate(validation_data)

            with self._cron as cron:
                item = self._find_cron_item(job_id_str, cron)

                if req.enabled is not None:
                    item.enable(req.enabled)

                if req.command:
                    item.set_command(req.command)

                if req.description or req.name:
                    desc = req.description or item.comment.split(' OPENVAIR')[0]
                    item.set_comment(f"{desc} OPENVAIR_JOB_ID:[{job_id_str}]")

                if req.cron_schedule:
                    item.setall(req.cron_schedule)

            return self.get(editing_data)

        except SchedulerDomainException as error:
            LOG.error(f'Failed to edit scheduled task: {error}')
            raise
