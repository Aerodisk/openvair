"""Pydantic schemas for the control-plane API.

This module defines request and response models used in the API layer
of the control-plane. The schemas describe input payloads for node
registration, heartbeat updates, and VM placement requests, as well as
output representations for nodes and placement decisions.

Classes:
    NodeRegisterIn: Input schema for registering a new cluster node.
    NodeOut: Output schema representing a cluster node.
    HeartbeatIn: Input schema for node heartbeat updates.
    VmPlacementRequest: Input schema for VM placement requests.
    VmPlacementDecision: Output schema with VM placement decision details.
"""

from uuid import UUID
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime

from pydantic import BaseModel


class NodeRegisterIn(BaseModel):
    """Input schema for registering a new cluster node.

    Attributes:
        hostname (str): Hostname of the node to register.
        ip (str): IP address of the node.
        roles (List[str]): Optional list of roles assigned to the node.
        labels (Dict[str, str]): Optional key-value labels for scheduling
            and classification.
    """

    hostname: str
    ip: str
    roles: List[str] = []
    labels: Dict[str, str] = {}


class NodeOut(BaseModel):
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


class HeartbeatIn(BaseModel):
    """Input schema for node heartbeat updates.

    Attributes:
        node_id (UUID): Identifier of the node sending the heartbeat.
        cpu_load (Optional[float]): Current CPU load on the node.
        mem_used_mb (Optional[int]): Current memory usage in MB.
    """

    node_id: UUID
    cpu_load: Optional[float] = None
    mem_used_mb: Optional[int] = None


class VmPlacementRequest(BaseModel):
    """Input schema for VM placement requests.

    Attributes:
        vcpu (int): Number of virtual CPUs requested for the VM.
        ram_mb (int): Amount of RAM in MB requested for the VM.
        disk_gb (Optional[int]): Disk space in GB requested for the VM.
        labels (Dict[str, str]): Optional key-value labels guiding
            placement decisions.
    """

    vcpu: int
    ram_mb: int
    disk_gb: Optional[int] = None
    labels: Dict[str, str] = {}


class VmPlacementDecision(BaseModel):
    """Output schema with VM placement decision details.

    Attributes:
        node_id (UUID): Identifier of the node selected for VM placement.
        reason (str): Human-readable explanation of the placement decision.
    """

    node_id: UUID
    reason: str


class ClusterEventOut(BaseModel):
    """Output schema representing a control-plane event.

    Attributes:
        id (int): Auto-incremented event identifier.
        node_id (Optional[UUID]): Related node identifier, if any.
        kind (str): Event kind (e.g., 'register', 'heartbeat', 'status_change').
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
