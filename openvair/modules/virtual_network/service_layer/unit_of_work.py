"""Unit of Work pattern implementation for virtual network management.

This module defines the abstract base class and its SQLAlchemy-based
implementation for managing the lifecycle of database operations related to
virtual networks.

Classes:
    - AbstractUnitOfWork: Abstract base class for unit of work pattern.
    - SqlAlchemyUnitOfWork: SQLAlchemy implementation of the unit of work
        pattern for virtual networks.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from openvair.modules.virtual_network.config import DEFAULT_SESSION_FACTORY
from openvair.modules.virtual_network.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for unit of work pattern.

    This class defines the interface for implementing the unit of work pattern
    in managing database operations related to virtual networks.

    Attributes:
        virtual_networks (AbstractRepository): Repository for managing virtual
            network objects.
        port_groups (AbstractRepository): Repository for managing port group
            objects.
        vlans (AbstractRepository): Repository for managing VLAN objects.
    """

    virtual_networks: repository.AbstractRepository
    port_groups: repository.AbstractRepository
    vlans: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Start a new database session and return the unit of work."""
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Close the database session and rollback if necessary."""
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy-based implementation of the unit of work pattern.

    This class manages the lifecycle of database operations using SQLAlchemy,
    ensuring that all changes to virtual network-related entities are committed
    or rolled back as a single unit of work.

    Attributes:
        session_factory (sessionmaker): SQLAlchemy session factory.
        session (Session): SQLAlchemy session.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker): SQLAlchemy session factory.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> AbstractUnitOfWork:
        """Start a new database session and return the unit of work."""
        self.session = self.session_factory()
        self.virtual_networks = repository.SqlAlchemyRepository(self.session)
        return super(SqlAlchemyUnitOfWork, self).__enter__()

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Close the database session and rollback if necessary."""
        super(SqlAlchemyUnitOfWork, self).__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
