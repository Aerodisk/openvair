"""Unit of Work implementation for scheduler module using SQLAlchemy."""

from typing import Type, Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SqlAlchemySession, sessionmaker

from openvair.modules.scheduler.adapters.repository import (
    SqlAlchemySchedulerRepository,
)

DATABASE_URL = 'postgresql+psycopg2://openvair:openvair@localhost/openvair'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class SchedulerSqlAlchemyUnitOfWork:
    """Unit of Work for managing scheduler database transactions."""

    def __init__(self) -> None:
        """Initialize scheduler Unit of Work."""
        self.session: SqlAlchemySession = cast(SqlAlchemySession, None)
        self.jobs: SqlAlchemySchedulerRepository = cast(
            SqlAlchemySchedulerRepository, None
        )

    def __enter__(self) -> 'SchedulerSqlAlchemyUnitOfWork':
        """Open DB session and repository for use inside context manager."""
        self.session = Session()
        self.jobs = SqlAlchemySchedulerRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Commit on success or roll back on error, then close session."""
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()
