"""ORM models for the control-plane module.

This module defines SQLAlchemy ORM models used by the control-plane
to represent cluster nodes and cluster-related events. These models
store information about the state, capacity, and allocation of nodes,
as well as structured events that describe lifecycle actions and state
changes within the cluster.

Classes:
    Base: Declarative base for control-plane ORM models.
    NodeStatus: Enumeration of possible cluster node statuses.
    ClusterNode: Database model representing a cluster node, including
        identification, status, and capacity details.
    ClusterEvent: Database model representing cluster-related events,
        providing audit and history of node state changes and actions.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import (
    Enum as SAEnum,
    Index,
    String,
    Integer,
    DateTime,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID, JSONB

if TYPE_CHECKING:
    from datetime import datetime


class Base(DeclarativeBase):
    """Declarative base for control-plane ORM models.

    This base class is used to declare SQLAlchemy ORM models related
    to the control-plane module. It isolates the control-plane models
    from other modules and provides a foundation for table mappings.
    """

    pass


# ---------- Enums ----------


class NodeStatus(str, Enum):
    """Enumeration of possible cluster node statuses.

    Attributes:
        ONLINE: Node is active and responding to heartbeats.
        OFFLINE: Node is unreachable or not responding.
        UNKNOWN: Node status has not been determined yet.
        CORDONED: Node is cordoned and not eligible for scheduling.
    """

    ONLINE = 'online'
    OFFLINE = 'offline'
    UNKNOWN = 'unknown'
    CORDONED = 'cordoned'


class ClusterNode(Base):
    """Database model representing a cluster node.

    This table stores identification, capacity, and status information
    for nodes participating in the cluster. It also maintains relations
    to cluster events that describe actions or state changes for this node.

    Attributes:
        id (uuid.UUID): Primary key, unique node identifier.
        hostname (str): Hostname of the node.
        ip (Optional[str]): IP address of the node.
        roles (List[str]): Assigned functional roles (compute, storage, etc.).
        labels (Dict[str, Any]): Arbitrary key-value labels for scheduling.
        status (NodeStatus): Current status of the node.
        last_seen (Optional[datetime]): Last heartbeat timestamp.
        capacity_cpu (Optional[int]): Total available vCPUs on the node.
        capacity_mem_mb (Optional[int]): Total available memory in MB.
        capacity_storage_gb (Optional[int]): Total available storage in GB.
        alloc_cpu (Optional[int]): Allocated vCPUs.
        alloc_mem_mb (Optional[int]): Allocated memory in MB.
        alloc_storage_gb (Optional[int]): Allocated storage in GB.
        events (List[ClusterEvent]): Related events linked to this node.
    """

    __tablename__ = 'cluster_nodes'
    __table_args__ = (
        UniqueConstraint('hostname', name='uq_cluster_nodes_hostname'),
        Index('ix_cluster_nodes_status', 'status'),
        Index('ix_cluster_nodes_last_seen', 'last_seen'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # базовая идентификация
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # роли/лейблы на будущее (compute/storage/etc.)
    roles: Mapped[List[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    labels: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    # состояние
    status: Mapped[NodeStatus] = mapped_column(
        SAEnum(NodeStatus, name='node_status', native_enum=True),
        nullable=False,
        default=NodeStatus.UNKNOWN,
    )
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ёмкости узла (опционально)
    capacity_cpu: Mapped[Optional[int]] = mapped_column(Integer)  # vCPU (шт.)
    capacity_mem_mb: Mapped[Optional[int]] = mapped_column(Integer)  # MB
    capacity_storage_gb: Mapped[Optional[int]] = mapped_column(Integer)  # GB

    # текущие аллокации (опционально)
    alloc_cpu: Mapped[Optional[int]] = mapped_column(Integer)
    alloc_mem_mb: Mapped[Optional[int]] = mapped_column(Integer)
    alloc_storage_gb: Mapped[Optional[int]] = mapped_column(Integer)

    # связи с событиями (если используем таблицу событий)  # noqa: RUF003
    events: Mapped[List['ClusterEvent']] = relationship(
        back_populates='node',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        """Return a string representation of the cluster node."""
        return (
            f'<ClusterNode id={self.id}'
            f'host={self.hostname}'
            f'status={self.status}>'
        )


class ClusterEvent(Base):
    """Database model representing a cluster-related event.

    This table stores structured events associated with cluster nodes,
    such as registration, heartbeats, status changes, or scheduling
    decisions. Events provide auditability and allow tracking of the
    cluster state over time.

    Attributes:
        id (int): Primary key, auto-incremented identifier of the event.
        node_id (Optional[uuid.UUID]): Foreign key referencing the node
            related to the event, nullable if not tied to a specific node.
        kind (str): Type of event (e.g., 'register', 'heartbeat',
            'status_change', 'schedule', 'migrate').
        payload (Dict[str, Any]): Arbitrary JSON payload with event details.
        message (Optional[str]): Human-readable description of the event.
        ts (datetime): Timestamp of the event creation.
        node (Optional[ClusterNode]): ORM relationship to the associated node.
    """

    __tablename__ = 'cluster_events'
    __table_args__ = (
        Index('ix_cluster_events_ts', 'ts'),
        Index('ix_cluster_events_node_id_ts', 'node_id', 'ts'),
        Index('ix_cluster_events_kind', 'kind'),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('cluster_nodes.id', ondelete='SET NULL'),
        nullable=True,
    )

    # тип события (например: 'register', 'heartbeat', 'status_change', 'schedule', 'migrate')  # noqa: E501, W505
    kind: Mapped[str] = mapped_column(String(64), nullable=False)

    # произвольный payload (детали)
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
    )

    node: Mapped[Optional[ClusterNode]] = relationship(back_populates='events')

    def __repr__(self) -> str:
        """Return a string representation of the cluster event."""
        return (
            f'<ClusterEvent id={self.id} '
            f'kind={self.kind} '
            f'node_id={self.node_id}>'
        )
