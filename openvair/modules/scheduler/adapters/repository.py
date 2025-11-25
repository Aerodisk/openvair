"""Repository implementation for scheduler jobs using SQLAlchemy."""

from typing import List, Optional

from sqlalchemy.orm import Session

from openvair.modules.scheduler.adapters.orm import SchedulerJob


class SqlAlchemySchedulerRepository:
    """Repository for managing SchedulerJob entities using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with SQLAlchemy session."""
        self.session = session

    def get_all(self) -> List[SchedulerJob]:
        """Retrieve all scheduler jobs."""
        return self.session.query(SchedulerJob).all()

    def get_by_id(self, job_id: int) -> Optional[SchedulerJob]:
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
