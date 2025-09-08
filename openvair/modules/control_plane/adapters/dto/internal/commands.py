"""Command/query DTOs for control-plane service operations.

These DTOs formalize inputs for service-layer methods and are validated by
Pydantic. They are not API schemas.
"""

from uuid import UUID
from typing import Dict, Optional

from pydantic import Field

from openvair.common.base_pydantic_models import BaseDTOModel


class RegisterNodeServiceCommandDTO(BaseDTOModel):
    """Command to register (or upsert) a node."""

    hostname: str = Field(..., min_length=1, max_length=255)
    ip: str
    roles: Optional[list] = None
    labels: Optional[dict] = None


class HeartbeatServiceCommandDTO(BaseDTOModel):
    """Command carrying heartbeat payload."""

    node_id: UUID
    cpu_load: Optional[float] = None
    mem_used_mb: Optional[int] = None


class PlacementRequestServiceDTO(BaseDTOModel):
    """Query for choosing placement target."""

    vcpu: int
    ram_mb: int
    disk_gb: Optional[int] = None
    labels: Dict[str, str] = Field(default_factory=dict)


class PlacementDecisionServiceDTO(BaseDTOModel):
    """Result of placement decision."""

    node_id: Optional[UUID]
    reason: str


class ListEventsQueryServiceDTO(BaseDTOModel):
    """Query for listing events with optional filters."""

    node_id: Optional[UUID] = None
    kind: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
