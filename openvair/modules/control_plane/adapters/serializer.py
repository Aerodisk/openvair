"""Serializers for the Control-Plane module (ORM <-> model DTO).

These serializers convert between SQLAlchemy ORM models and internal model DTOs.
They do NOT work with command DTOs and do NOT touch API schemas directly.
"""

from typing import Type

from openvair.modules.control_plane.adapters.orm import (
    ClusterNode as NodeORM,
    ClusterEvent as EventORM,
)
from openvair.common.serialization.base_serializer import BaseSerializer
from openvair.modules.control_plane.adapters.dto.internal.models import (
    ApiNodeModelDTO,
    NodeCreateModelDTO,
    ClusterEventModelDTO,
)


class NodeApiSerializer(BaseSerializer[ApiNodeModelDTO, NodeORM]):
    """ORM <-> DTO serializer for cluster nodes (internal view)."""

    dto_class: Type[ApiNodeModelDTO] = ApiNodeModelDTO
    orm_class: Type[NodeORM] = NodeORM


class NodeCreateSerializer(BaseSerializer[NodeCreateModelDTO, NodeORM]):
    """DTO(Create) -> ORM serializer for node creation/upsert."""

    dto_class: Type[NodeCreateModelDTO] = NodeCreateModelDTO
    orm_class: Type[NodeORM] = NodeORM


class ClusterEventSerializer(BaseSerializer[ClusterEventModelDTO, EventORM]):
    """ORM <-> DTO serializer for control-plane events (internal view)."""

    dto_class: Type[ClusterEventModelDTO] = ClusterEventModelDTO
    orm_class: Type[EventORM] = EventORM
