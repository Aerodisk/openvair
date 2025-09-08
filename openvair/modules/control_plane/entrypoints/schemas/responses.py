"""Response schemas for control-plane API endpoints.

This module defines Pydantic models representing structured responses
returned by the control-plane API. These schemas ensure a consistent
and validated format for outgoing data.

Classes:
    VmPlacementResponse: Output schema with VM placement decision details.
    ClusterEventResponse: Output schema representing a control-plane event.
    NodeResponse: Output schema representing a cluster node.
"""

from uuid import UUID
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime

from pydantic import BaseModel


class VmPlacementResponse(BaseModel):
    """Output schema with VM placement decision details.

    Attributes:
        node_id (UUID): Identifier of the node selected for VM placement.
        reason (str): Human-readable explanation of the placement decision.
    """

    node_id: UUID
    reason: str


class ClusterEventResponse(BaseModel):
    """Output schema representing a control-plane event.

    Attributes:
        id (int): Auto-incremented event identifier.
        node_id (Optional[UUID]): Related node identifier, if any.
        kind (str): Event kind (e.g., 'register', 'heartbeat',
            'status_change').
        payload (Dict[str, Any]): Structured event details.
        message (Optional[str]): Optional human-readable message.
        ts (datetime): Event timestamp (UTC).
    """

    id: int
    node_id: Optional[UUID]
    kind: str
    payload: Dict[str, Any]
    message: Optional[str]
    ts: datetime


class NodeResponse(BaseModel):
    """Output schema representing a cluster node.

    Attributes:
        id (UUID): Unique identifier of the node.
        hostname (str): Hostname of the node.
        ip (str): IP address of the node.
        status (Literal): Current node status: "online", "offline",
            "unknown", or "cordoned".
        roles (List[str]): Roles assigned to the node.
        labels (Dict[str, str]): Arbitrary labels associated with the node.
        last_seen (datetime): Timestamp of the last heartbeat received.
    """

    id: UUID
    hostname: str
    ip: str
    status: Literal['online', 'offline', 'unknown', 'cordoned']
    roles: List[str]
    labels: Dict[str, str]
    last_seen: datetime
