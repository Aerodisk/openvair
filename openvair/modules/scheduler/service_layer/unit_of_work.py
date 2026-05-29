"""Unit of Work implementation for the scheduler module.

This module defines a SQLAlchemy-based Unit of Work for managing
scheduler-related transactions and repositories.

Classes:
    - SchedulerSqlAlchemyUnitOfWork: Unit of Work for the scheduler module.
"""

from sqlalchemy.orm import sessionmaker

from openvair.modules.scheduler.config import DEFAULT_SESSION_FACTORY
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.scheduler.adapters.repository import (
    SqlAlchemySchedulerRepository,
)


class SchedulerSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Unit of Work for the scheduler module.

    This class manages database transactions for scheduler, ensuring consistency
    by committing or rolling back operations.

    Attributes:
        jobs (SqlAlchemySchedulerRepository): Repository for job entities.
    """

    def __init__(
        self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY
    ) -> None:
        """Initializes the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): SQLAlchemy session factory.
                Defaults to DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initialize repositories for the scheduler module."""
        self.jobs = SqlAlchemySchedulerRepository(self.session)
