"""Factories for scheduler domain modules

This module defines an abstract factory class for inheriting concrete
factories based on scheduler types
"""

import abc
from typing import Dict, ClassVar, Optional, cast

from crontab import CronTab
from pydantic import Field, BaseModel

from openvair.modules.scheduler.domain.base import BaseScheduler
from openvair.modules.scheduler.domain.cron_jobs.cron_job import (
    CronJobScheduler,
)


class DomainSchedulerModelDTO(BaseModel):
    """Заглушка"""

    scheduler_type: str = Field(..., alias='type')
    user: Optional[str] = None


class AbstractSchedulerFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating scheduler instances."""

    def __call__(self, scheduler_data: Dict) -> BaseScheduler:
        """Creates a scheduler instance from provided data.

        Args:
            scheduler_data (Dict): Data for creating a scheduler.

        Returns:
            BaseScheduler: The created scheduler instance.
        """
        return self.get_scheduler(scheduler_data)

    @abc.abstractmethod
    def get_scheduler(self, scheduler_data: Dict) -> BaseScheduler:
        """Returns a scheduler instance based on the provided data.

        Args:
            scheduler_data (Dict): Data for creating a scheduler.

        Returns:
            BaseScheduler: The created scheduler instance.
        """
        ...


class SchedulerFactory(AbstractSchedulerFactory):
    """Concrete factory for scheduler creation."""

    _scheduler_classes: ClassVar = {
        'system_cron': CronJobScheduler,
    }

    def get_scheduler(self, scheduler_data: Dict) -> BaseScheduler:
        """Creates and returns a concrete scheduler instance.

        Selects the appropriate implementation based on `scheduler_type`
        (e.g., 'system_cron') and initializes it with validated data.

        Args:
            scheduler_data (Dict): Raw dictionary to build a domain scheduler.
                Example: {'type': 'system_cron', 'user': 'root'}

        Returns:
            BaseScheduler: Instantiated domain scheduler.

        Raises:
            ValueError: If an unknown scheduler type is provided.
        """
        dto = DomainSchedulerModelDTO.model_validate(scheduler_data)

        scheduler_class = self._scheduler_classes.get(dto.scheduler_type)
        if not scheduler_class:
            error_msg = f"Unknown scheduler type: '{dto.scheduler_type}'"
            raise ValueError(error_msg)

        cron_obj = CronTab(user=dto.user)
        scheduler_manager = scheduler_class(cron_obj=cron_obj)

        return cast(BaseScheduler, scheduler_manager)
