"""Module for handling event repository operations using the repository pattern.

This module defines an abstract repository for events and a concrete
implementation using SQLAlchemy for interacting with the event store.

Classes:
    AbstractRepository: An abstract base class for event repositories.
    SqlAlchemyRepository: A concrete implementation of AbstractRepository using
        SQLAlchemy.
"""

import abc
from uuid import UUID
from typing import TYPE_CHECKING, List

from sqlalchemy import desc

from openvair.modules.event_store.adapters.orm import Events

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for event repositories.

    This class defines the interface for repositories managing `Events`.
    Subclasses must implement the abstract methods to handle adding and
    retrieving events.
    """

    def add(self, event: Events) -> None:
        """Add a new event to the repository.

        Args:
            event (Events): The event to add.
        """
        self._add(event)

    def get_all(self) -> List[Events]:
        """Retrieve all events from the repository.

        Returns:
            List[Events]: A list of all events.
        """
        return self._get_all()

    def get_all_by_module(self, module_name: str) -> List[Events]:
        """Retrieve all events for a specific module.

        Args:
            module_name (str): The name of the module.

        Returns:
            List[Events]: A list of events for the specified module.
        """
        return self._get_all_by_module(module_name)

    def get_last_events(self, limit: int = 25) -> List[Events]:
        """Retrieve the most recent events from the repository.

        Args:
            limit (int): The maximum number of events to retrieve.
                Defaults to 25.

        Returns:
            List[Events]: A list of the most recent events.
        """
        return self._get_last_events(limit)

    @abc.abstractmethod
    def _add(self, event: Events) -> None:
        """Add a new event to the repository.

        Args:
            event (Events): The event to add.

        Raises:
            NotImplementedError: This method must be overridden by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List[Events]:
        """Retrieve all events from the repository.

        Returns:
            List[Events]: A list of all events.

        Raises:
            NotImplementedError: This method must be overridden by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all_by_module(self, module_name: str) -> List[Events]:
        """Retrieve all events for a specific module.

        Args:
            module_name (str): The name of the module.

        Returns:
            List[Events]: A list of events for the specified module.

        Raises:
            NotImplementedError: This method must be overridden by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_last_events(self, limit: int = 25) -> List[Events]:
        """Retrieve the most recent events from the repository.

        Args:
            limit (int): The maximum number of events to retrieve.
                Defaults to 25.

        Returns:
            List[Events]: A list of the most recent events.

        Raises:
            NotImplementedError: This method must be overridden by subclasses.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """Concrete implementation of AbstractRepository using SQLAlchemy.

    This class provides methods to interact with the `Events` table in the
    database using SQLAlchemy ORM.
    """

    def __init__(self, session: 'Session') -> None:
        """Initialize the repository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
        """
        super(SqlAlchemyRepository, self).__init__()
        self.session: Session = session

    def _get(self, event_id: UUID) -> Events:
        """Retrieve an event by its ID.

        Args:
            event_id (UUID): The unique identifier of the event.

        Returns:
            Events: The event with the specified ID.
        """
        return self.session.query(Events).filter_by(id=event_id).one()

    def _add(self, event: Events) -> None:
        """Add a new event to the repository.

        Args:
            event (Events): The event to add.
        """
        self.session.add(event)

    def _get_all(self) -> List[Events]:
        """Retrieve all events from the repository.

        Returns:
            List[Events]: A list of all events.
        """
        return self.session.query(Events).all()

    def _get_all_by_module(self, module_name: str) -> List[Events]:
        """Retrieve all events for a specific module.

        Args:
            module_name (str): The name of the module.

        Returns:
            List[Events]: A list of events for the specified module.
        """
        return self.session.query(Events).filter_by(module=module_name).all()

    def _get_last_events(self, limit: int = 25) -> List[Events]:
        """Retrieve the most recent events from the repository.

        Args:
            limit (int): The maximum number of events to retrieve.
                Defaults to 25.

        Returns:
            List[Events]: A list of the most recent events.
        """
        return self.session.query(Events).order_by(desc(Events.id)).limit(limit)
