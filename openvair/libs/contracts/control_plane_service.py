from uuid import UUID  # noqa: D100
from typing import Dict, Optional

from pydantic import Field

from openvair.common.base_pydantic_models import BaseDTOModel


class RegisterNodeServiceCommand(BaseDTOModel):
    """Command to register (or upsert) a node."""

    hostname: str = Field(..., min_length=1, max_length=255)
    ip: str
    roles: Optional[list] = None
    labels: Optional[dict] = None


class HeartbeatServiceCommand(BaseDTOModel):
    """Command carrying heartbeat payload."""

    node_id: UUID
    cpu_load: Optional[float] = None
    mem_used_mb: Optional[int] = None


class PlacementRequestServiceCommand(BaseDTOModel):
    """Query for choosing placement target."""

    vcpu: int
    ram_mb: int
    disk_gb: Optional[int] = None
    labels: Dict[str, str] = Field(default_factory=dict)
