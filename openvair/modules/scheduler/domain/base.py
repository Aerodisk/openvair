# mypy: disable-error-code="no-any-unimported, unused-ignore"

"""Base classes for scheduler domain models.

This module defines the `BaseScheduler` abstract class, which serves
as the foundation for implementing specific scheduler types
(e.g., SystemCronScheduler). It declares the required interface
and shared fields for managing scheduled tasks.
"""

import abc
import datetime
from uuid import UUID
from typing import Any, Dict, Union, Optional

from crontab import CronItem
from pydantic import Field, BaseModel, ConfigDict


class JobMetadata(BaseModel):
    """Metadata container for a scheduled task in the scheduler domain.

    This class encapsulates the physical cron task (CronItem) along with
    domain-specific information such as naming, audit timestamps, and
    relational links to other job versions or related tasks.

    Attributes:
        cron_item (CronItem): The underlying crontab item instance.
        name (str): Human-readable identifier for the task.
        created_at (datetime.datetime): Timestamp when the task was created.
        updated_at (Optional[datetime.datetime]): Timestamp of the last
            modification. Defaults to None.
        previous_id (UUID | None): Identifier of the preceding task version
            or related job in a sequence.
        next_id (UUID | None): Identifier of the succeeding task version
            or related job in a sequence.

    Note:
        The `model_config` allows `arbitrary_types_allowed` to support
        the `CronItem` type, which is not a native Pydantic model.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    cron_item: CronItem
    name: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = Field(default=None)
    previous_id: Union[UUID, None] = Field(default=None)
    next_id: Union[UUID, None] = Field(default=None)


class BaseScheduler(metaclass=abc.ABCMeta):
    """Abstract base class for scheduler domain models.

    This class defines the interface for all scheduler operations such as
    creation, editing, deletion, and retrieval of scheduled tasks (cron jobs).
    Concrete implementations must implement all abstract methods.
    """

    def __init__(self) -> None:
        """Initialize the BaseScheduler."""
        self.jobs: Dict[UUID, JobMetadata] = {}

    @abc.abstractmethod
    def create(self, creation_data: dict[str, Any]) -> dict[str, Any]:
        """Create a scheduled task.

        Args:
            creation_data (Dict[str, Any]): Data required for task creation,
                e.g., {'schedule': '0 0 * * *', 'command': '/bin/true',
                'comment': 'my-job-id'}.

        Returns:
            Dict[str, Any]: A dictionary representation of the created task.
        """
        ...

    @abc.abstractmethod
    def get(self, data: dict[str, Any]) -> dict[str, Any]:
        """Retrieve a single scheduled task by its unique identifier.

        Args:
            data (Dict[str, Any]): Dictionary containing 'job_id'.

        Returns:
            Dict[str, Any]: A dictionary representation of the found task.

        Raises:
            CronJobNotFound: If a task with the given ID is not found.
        """
        ...

    @abc.abstractmethod
    def list_all(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve all scheduled tasks managed by this scheduler.

        Args:
            data (Dict[str, Any]): Dictionary with request data (can be empty).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
            represents a scheduled task.
        """
        ...

    @abc.abstractmethod
    def edit(self, editing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a scheduled task.

        Args:
            editing_data (Dict[str, Any]): New data for the task.

        Returns:
            Dict[str, Any]: A dictionary representation of the updated task.

        Raises:
            CronJobNotFound: If a task with the given ID is not found.
        """
        ...

    @abc.abstractmethod
    def delete(self, data: dict[str, Any]) -> None:
        """Delete a scheduled task by its unique identifier.

        Args:
            data (Dict[str, Any]): Dictionary containing 'job_id'.

        Raises:
            CronJobNotFound: If a task with the given ID is not found.
        """
        ...
