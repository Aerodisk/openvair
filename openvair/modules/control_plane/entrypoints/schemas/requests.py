"""Request schemas for control-plane API endpoints.

This module defines Pydantic models representing incoming request
payloads for cluster-related API operations. These schemas validate
user input before it reaches the service layer.

Classes:
    HeartbeatRequest: Input schema for node heartbeat updates.
    VmPlacementRequest: Input schema for VM placement requests.
    NodeRegisterRequest: Input schema for registering new cluster nodes.
"""

from uuid import UUID
from typing import Dict, List, Optional

from pydantic import BaseModel


class HeartbeatRequest(BaseModel):
    """Input schema for node heartbeat updates.

    Attributes:
        node_id (UUID): Identifier of the node sending the heartbeat.
        cpu_load (Optional[float]): Current CPU load of the node.
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


class NodeRegisterRequest(BaseModel):
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
