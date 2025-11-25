"""Module for managing unit of work for dashboard operations.

This module defines abstract and concrete unit of work classes for handling
operations related to retrieving Prometheus data for the dashboard.

Classes:
    AbstractUnitOfWork: Abstract base class for unit of work.
    PrometheusUnitOfWork: Concrete implementation for Prometheus.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.modules.dashboard.config import DEFAULT_SESSION_FACTORY
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.dashboard.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class PrometheusUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Concrete unit of work for Prometheus.

    This class provides the implementation for managing Prometheus repository
    interactions, ensuring proper initialization and cleanup of resources.
    """

    def __init__(
        self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY
    ) -> None:
        """Initialize the PrometheusUnitOfWork.

        This constructor sets up the necessary components for the
        PrometheusUnitOfWork, ensuring proper initialization of the base
        class.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes prometheus repository for the dashboard module."""
        self.prometheus = repository.PrometheusRepository()
