"""Module for handling event repository operations using the repository pattern.

This module implements the repository pattern to manage Event entities
in the database using SQLAlchemy.
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import desc

from openvair.modules.event_store.adapters.orm import Events
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class EventStoreSqlAlchemyRepository(BaseSqlAlchemyRepository[Events]):
    """Repository for managing event entities.

    This class provides CRUD operations for the Events model using SQLAlchemy.
    """

    def __init__(self, session: 'Session') -> None:
        """Initialize the repository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
        """
        super().__init__(session, Events)

    def get_all_by_module(self, module_name: str) -> List[Events]:
        """Retrieve all events for a specific module.

        Args:
            module_name (str): The name of the module.

        Returns:
            List[Events]: A list of events for the specified module.
        """
        return self.session.query(Events).filter_by(module=module_name).all()

    def get_last_events(self, limit: int = 25) -> List[Events]:
        """Retrieve the most recent events from the repository.

        Args:
            limit (int): The maximum number of events to retrieve.
                Defaults to 25.

        Returns:
            List[Events]: A list of the most recent events.
        """
        return (
            self.session.query(Events)
            .order_by(desc(Events.id))
            .limit(limit)
            .all()
        )
