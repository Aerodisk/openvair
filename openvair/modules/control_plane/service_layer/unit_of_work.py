"""Unit of Work for the control-plane module.

This UoW wires SQLAlchemy session management to the repositories used by
the control-plane (nodes and events). Use it in services to group DB
operations into a single transactional scope.

Classes:
    ControlPlaneUnitOfWork: SQLAlchemy-based UoW exposing repositories:
        - nodes: ClusterNodeRepository
        - events: ClusterEventRepository
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.control_plane.adapters.repository import (
    ClusterNodeRepository,
    ClusterEventRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class ControlPlaneUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """SQLAlchemy Unit of Work for control-plane."""

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initializes the Unit of Work for the control-plane module.

        Args:
            session_factory (sessionmaker): Factory for creating new SQLAlchemy
                sessions. Each session is bound to the repositories (nodes and
                events) and managed by this Unit of Work.
        """
        super().__init__(session_factory)
        self.nodes: ClusterNodeRepository
        self.events: ClusterEventRepository

    def _init_repositories(self) -> None:
        """Initializes repositories bound to the active session."""
        self.nodes = ClusterNodeRepository(self.session)
        self.events = ClusterEventRepository(self.session)
