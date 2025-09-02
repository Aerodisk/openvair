"""Repositories for the control-plane module.

This module contains SQLAlchemy-based repositories for cluster nodes and
cluster events, built on top of the project's BaseSqlAlchemyRepository.

Classes:
    ClusterNodeRepository: Data access for ClusterNode entities.
    ClusterEventRepository: Data access for ClusterEvent entities, including
        append, list, and retention cleanup helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
from datetime import datetime, timezone, timedelta

from sqlalchemy import delete, select

from openvair.modules.control_plane.adapters.orm import (
    NodeStatus,
    ClusterNode,
    ClusterEvent,
)
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.orm import Session


class ClusterNodeRepository(BaseSqlAlchemyRepository[ClusterNode]):
    """Repository for ClusterNode entities.

    Provides helpers commonly needed by the control-plane MVP:
    - fetch by hostname,
    - filter by status,
    - update last_seen and status,
    - basic listings.
    """

    def __init__(self, session: Session) -> None:
        """Initializes the ClusterNodeRepository.

        Args:
            session (Session): Active SQLAlchemy session used for all
                database operations within this repository.
        """
        super().__init__(session=session, model_cls=ClusterNode)

    def get_by_hostname(self, hostname: str) -> Optional[ClusterNode]:
        """Retrieve a node by its hostname.

        Args:
            hostname (str): Hostname of the node to search.

        Returns:
            Optional[ClusterNode]: The node if found, otherwise None.
        """
        stmt = select(ClusterNode).where(ClusterNode.hostname == hostname)
        return self.session.scalars(stmt).first()

    def list_by_status(self, status: NodeStatus) -> List[ClusterNode]:
        """Retrieve nodes by a specific status.

        Args:
            status (NodeStatus): Status to filter nodes by
                (e.g., ONLINE, OFFLINE).

        Returns:
            List[ClusterNode]: List of nodes matching the given status.
        """
        stmt = select(ClusterNode).where(ClusterNode.status == status)
        return list(self.session.scalars(stmt).all())

    def list_ordered_by_last_seen_desc(
        self,
        limit: int = 100,
    ) -> List[ClusterNode]:
        """Retrieve nodes ordered by last_seen timestamp in descending order.

        Args:
            limit (int): Maximum number of nodes to return. Defaults to 100.

        Returns:
            List[ClusterNode]: Nodes ordered by last_seen, newest first.
        """
        stmt = (
            select(ClusterNode)
            .order_by(ClusterNode.last_seen.desc().nullslast())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def update_last_seen(
        self,
        node_id: UUID,
        *,
        when: Optional[datetime] = None,
    ) -> None:
        """Update the last_seen timestamp for a node.

        Args:
            node_id (UUID): Identifier of the node to update.
            when (Optional[datetime]): New timestamp value. If None,
                the current UTC time will be used.

        Raises:
            EntityNotFoundError: If the node with the given ID does not exist.
        """
        node = self.get_or_fail(node_id)
        node.last_seen = when or datetime.now(timezone.utc)
        self.session.flush()

    def set_status(
        self,
        node_id: UUID,
        status: NodeStatus,
    ) -> None:
        """Set the status of a node.

        Args:
            node_id (UUID): Identifier of the node to update.
            status (NodeStatus): New status value for the node.

        Raises:
            EntityNotFoundError: If the node with the given ID does not exist.
        """
        node = self.get_or_fail(node_id)
        node.status = status
        self.session.flush()


class ClusterEventRepository(BaseSqlAlchemyRepository[ClusterEvent]):
    """Repository for ClusterEvent entities.

    Includes convenience methods for appending events, listing recent events,
    filtering by node/kind, and purging by retention policy.
    """

    def __init__(self, session: Session) -> None:
        """Initializes the ClusterEventRepository.

        Args:
            session (Session): Active SQLAlchemy session used for all
                database operations within this repository.
        """
        super().__init__(session=session, model_cls=ClusterEvent)

    def append(
        self,
        *,
        kind: str,
        node_id: Optional[UUID] = None,
        payload: Optional[dict] = None,
        message: Optional[str] = None,
        ts: Optional[datetime] = None,
    ) -> ClusterEvent:
        """Append a new event to the database.

        Args:
            kind (str): Type of event (e.g., 'register', 'heartbeat').
            node_id (Optional[UUID]): Related node identifier, if any.
            payload (Optional[dict]): Arbitrary JSON payload with event details.
            message (Optional[str]): Optional human-readable message.
            ts (Optional[datetime]): Timestamp of the event. Defaults to now
                UTC.

        Returns:
            ClusterEvent: The newly created event entity with populated ID.
        """
        evt = ClusterEvent(
            node_id=node_id,
            kind=kind,
            payload=payload or {},
            message=message,
            ts=ts or datetime.now(timezone.utc),
        )
        self.add(evt)  # Base adds + flushes
        return evt

    # ---------- read ----------

    def list_recent(
        self,
        *,
        limit: int = 100,
    ) -> List[ClusterEvent]:
        """Retrieve the most recent events.

        Args:
            limit (int): Maximum number of events to return. Defaults to 100.

        Returns:
            List[ClusterEvent]: Events ordered by timestamp descending.
        """
        stmt = (
            select(ClusterEvent).order_by(ClusterEvent.ts.desc()).limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def list_by_node(
        self,
        node_id: UUID,
        *,
        limit: int = 100,
    ) -> List[ClusterEvent]:
        """Retrieve recent events for a specific node.

        Args:
            node_id (UUID): Identifier of the node whose events to retrieve.
            limit (int): Maximum number of events to return. Defaults to 100.

        Returns:
            List[ClusterEvent]: Events for the given node, newest first.
        """
        stmt = (
            select(ClusterEvent)
            .where(ClusterEvent.node_id == node_id)
            .order_by(ClusterEvent.ts.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def list_by_kind(
        self,
        kind: str,
        *,
        limit: int = 100,
    ) -> List[ClusterEvent]:
        """Retrieve recent events by kind.

        Args:
            kind (str): Event kind to filter (e.g., 'status_change').
            limit (int): Maximum number of events to return. Defaults to 100.

        Returns:
            List[ClusterEvent]: Events of the given kind, newest first.
        """
        stmt = (
            select(ClusterEvent)
            .where(ClusterEvent.kind == kind)
            .order_by(ClusterEvent.ts.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def purge_older_than(
        self,
        *,
        days: int,
    ) -> int:
        """Delete events older than the specified number of days.

        Args:
            days (int): Age threshold in days. Events older than this will be
                permanently deleted.

        Returns:
            int: Number of rows deleted (may be 0 if nothing matched).
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(ClusterEvent).where(ClusterEvent.ts < cutoff)
        res = self.session.execute(stmt)
        return res.rowcount or 0
