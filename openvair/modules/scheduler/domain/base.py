"""Base classes for scheduler domain models.

This module defines the `BaseScheduler` abstract class, which serves as the
foundation for implementing specific scheduler types (e.g., SystemCronScheduler).
It declares the required interface and shared fields for managing scheduled tasks.
"""

import abc
import datetime
from uuid import UUID
from typing import Any, Optional

from crontab import CronTab, CronItem
from pydantic import Field, BaseModel


class JobMetadata(BaseModel):
    cron_item: CronItem
    name: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = Field(default=None)
    previous_id: UUID | None = Field(default=None)
    next_id: UUID | None = Field(default=None)


class BaseScheduler(metaclass=abc.ABCMeta):
    """Abstract base class for scheduler domain models.

    This class defines the interface for all scheduler operations such as
    creation, editing, deletion, and retrieval of scheduled tasks (cron jobs).
    Concrete implementations must implement all abstract methods.
    """

    def __init__(self, cron_obj: CronTab) -> None:
        self._cron = cron_obj
        self.jobs: dict[UUID, JobMetadata] = {}

    @abc.abstractmethod
    def create(self, creation_data: dict[str, Any]) -> dict[str, Any]:
        """Create a scheduled task.

        Args:
            creation_data (dict[str, Any]): Data required for task creation,
                e.g., {'schedule': '0 0 * * *', 'command': '/bin/true', 'comment': 'my-job-id'}.

        Returns:
            dict[str, Any]: A dictionary representation of the created task.
        """
        ...

    @abc.abstractmethod
    def get(self, job_id: str) -> dict[str, Any]:
        """Retrieve a single scheduled task by its unique identifier.

        Args:
            job_id (str): The unique identifier (e.g., comment) of the task.

        Returns:
            dict[str, Any]: A dictionary representation of the found task.

        Raises:
            CronJobNotFound: If a task with the given ID is not found.
        """
        ...

    @abc.abstractmethod
    def list_all(self) -> list[dict[str, Any]]:
        """Retrieve all scheduled tasks managed by this scheduler.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, where each dictionary
            represents a scheduled task.
        """
        ...

    @abc.abstractmethod
    def edit(self, editing_data: dict[str, Any]) -> dict[str, Any]:
        """Edit a scheduled task.

        Args:
            editing_data (dict[str, Any]): New data for the task.

        Returns:
            dict[str, Any]: A dictionary representation of the updated task.

        Raises:
            CronJobNotFound: If a task with the given ID is not found.
        """
        ...

    @abc.abstractmethod
    def delete(self, job_id: str) -> None:
        """Delete a scheduled task by its unique identifier.

        Args:
            job_id (str): The unique identifier of the task to delete.

        Raises:
            CronJobNotFound: If a task with the given ID is not found.
        """
        ...
