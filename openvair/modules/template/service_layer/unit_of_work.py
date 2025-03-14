"""Unit of Work implementation for the template module.

This module defines a SQLAlchemy-based Unit of Work for managing
template-related transactions and repositories.

Classes:
    - TemplateSqlAlchemyUnitOfWork: Unit of Work for the template module.
"""

from sqlalchemy.orm import sessionmaker

from openvair.modules.storage.config import DEFAULT_SESSION_FACTORY
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.template.adapters.repository import (
    TemplateSqlAlchemyRepository,
)


class TemplateSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Unit of Work for the template module.

    This class manages database transactions for templates, ensuring consistency
    by committing or rolling back operations.

    Attributes:
        templates (TemplateSqlAlchemyRepository): Repository for template
            entities.
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
        """Initializes repositories for the template module."""
        self.templates = TemplateSqlAlchemyRepository(self.session)
