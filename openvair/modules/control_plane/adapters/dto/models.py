"""DTOs for internal data structures in the control-plane module.

These models are used between ORM and service/domain layers and are NOT API
schemas. API layer should convert to its own request/response schemas.
"""

from uuid import UUID
from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field

from openvair.common.base_pydantic_models import BaseDTOModel
from openvair.modules.control_plane.adapters.orm import NodeStatus


class ApiNodeModelDTO(BaseDTOModel):
    """DTO representing a cluster node inside service/domain layers."""

    id: UUID
    hostname: str
    ip: Optional[str]
    status: NodeStatus
    roles: List[str]
    labels: Dict[str, str]
    last_seen: Optional[datetime]


class NodeCreateModelDTO(BaseDTOModel):
    """DTO for creating/upserting a cluster node at the service layer."""

    hostname: str
    ip: str
    roles: List[str] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)


class ClusterEventModelDTO(BaseDTOModel):
    """DTO representing a control-plane event for internal use."""

    id: int
    node_id: Optional[UUID]
    kind: str
    payload: Dict[str, object]
    message: Optional[str]
    ts: datetime
