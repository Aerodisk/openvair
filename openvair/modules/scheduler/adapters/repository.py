"""SQLAlchemy repository for the scheduler module.

This module implements the repository pattern to manage job entities
in the database using SQLAlchemy.
"""

from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)


class SchedulerSqlAlchemyRepository(BaseSqlAlchemyRepository[SchedulerJob]):
    """Repository for managing scheduler jobs entities.

    This class provides CRUD operations for the jobs using SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with SQLAlchemy session."""
        super().__init__(session, SchedulerJob)

    def get_all(self) -> List[SchedulerJob]:
        """Retrieve all scheduler jobs."""
        return self.session.query(SchedulerJob).all()

    def get_by_id(self, job_id: UUID) -> Optional[SchedulerJob]:
        """Retrieve scheduler job by its ID."""
        return (
            self.session.query(SchedulerJob)
            .filter(SchedulerJob.id == job_id)
            .first()
        )

    def get_by_name(self, job_name: str) -> Optional[SchedulerJob]:
        """Retrieve scheduler job by its name."""
        return (
            self.session.query(SchedulerJob)
            .filter(SchedulerJob.name == job_name)
            .first()
        )

    def add(self, job: SchedulerJob) -> None:
        """Add a new job to session."""
        self.session.add(job)

    def delete(self, job: SchedulerJob) -> None:
        """Delete job from session."""
        self.session.delete(job)


class SqlAlchemySchedulerRepository(SchedulerSqlAlchemyRepository):
    """Compatibility alias for repository naming in requirements."""

    def add(self, job: SchedulerJob) -> None:
        """Add a scheduler job entity."""
        super().add(job)

    def get(self, job_id: UUID) -> Optional[SchedulerJob]:
        """Get scheduler job entity by identifier."""
        return super().get_by_id(job_id)

    def get_all(self) -> List[SchedulerJob]:
        """Get all scheduler job entities."""
        return super().get_all()

    def update(self, job: SchedulerJob) -> None:
        """Persist updated scheduler job entity in current session."""
        self.session.add(job)

    def delete(self, job: SchedulerJob) -> None:
        """Delete scheduler job entity."""
        super().delete(job)

    def get_by_name(self, job_name: str) -> Optional[SchedulerJob]:
        """Get scheduler job by unique name."""
        return super().get_by_name(job_name)
