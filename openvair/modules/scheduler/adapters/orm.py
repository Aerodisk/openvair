"""ORM models for scheduler module."""

import uuid
from typing import Union
from datetime import datetime

from sqlalchemy import Text, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""


class SchedulerJob(Base):
    """ORM class representing a job.

    Attributes:
        id: Unique identifier of the job.
        name: Unique name of the job.
        description: Optional description.
        cron_schedule: Cron schedule expression.
        command: Cron job command.
        enabled: State of the job (enabled / disabled).
        created_at: Timestamp when the job was created.
        updated_at: Timestamp when the job was lastly updated.
        last_run: Timestamp when the job ran last time.
        next_run: Timestamp when the job is going to run next time.

    """

    __tablename__ = 'scheduler_jobs'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Union[str, None]] = mapped_column(Text, nullable=True)
    cron_schedule: Mapped[str] = mapped_column(String(255), nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    last_run: Mapped[Union[datetime, None]] = mapped_column(
        DateTime, nullable=True
    )
    next_run: Mapped[Union[datetime, None]] = mapped_column(
        DateTime, nullable=True
    )
