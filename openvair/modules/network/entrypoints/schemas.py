"""Schemas for network interfaces and bridges.

This module defines the Pydantic models (schemas) used for validating and
serializing network interface and bridge data in the API.

Schemas:
    InterfaceExtraSpecs: Additional specifications for network interfaces.
    Interface: Schema representing a network interface.
    BridgeDelete: Schema for deleting a bridge.
    BridgeCreate: Schema for creating a new bridge.
    BridgeCreateResponse: Schema for the response after creating a bridge.
    ListOfInterfaces: Schema for a list of network interfaces.
"""

from typing import List, Optional

from pydantic import BaseModel


class InterfaceExtraSpecs(BaseModel):
    """Additional specifications for network interfaces.

    Attributes:
        slot_port (Optional[str]): The slot and port information.
        duplex (Optional[str]): The duplex mode of the interface.
    """

    slot_port: Optional[str]
    duplex: Optional[str]


class Interface(BaseModel):
    """Schema representing a network interface.

    Attributes:
        id (str): The unique identifier of the interface.
        name (str): The name of the interface.
        mac (str): The MAC address of the interface.
        ip (Optional[str]): The IP address of the interface.
        netmask (Optional[str]): The netmask of the interface.
        inf_type (str): The type of the interface (e.g., physical, virtual).
        power_state (str): The power state of the interface (e.g., on, off).
        status (Optional[str]): The status of the interface.
        mtu (Optional[int]): The Maximum Transmission Unit size.
        speed (Optional[int]): The speed of the interface.
        interface_extra_specs (Optional[InterfaceExtraSpecs]): Additional
            specifications for the interface.
    """

    id: str
    name: str
    mac: str
    ip: Optional[str]
    netmask: Optional[str]
    inf_type: str
    power_state: str
    status: Optional[str]
    mtu: Optional[int]
    speed: Optional[int]
    interface_extra_specs: Optional[InterfaceExtraSpecs]


class BridgeDelete(BaseModel):
    """Schema for deleting a bridge.

    Attributes:
        data (List[Interface]): The list of interfaces to delete.
    """

    data: List[Interface]


class BridgeCreate(BaseModel):
    """Schema for creating a new bridge.

    Attributes:
        ip (Optional[str]): The IP address of the bridge.
        name (str): The name of the bridge.
        type (str): The type of the bridge (e.g., OVS, Linux bridge).
        interfaces (List[Interface]): The list of interfaces associated with
            the bridge.
        status (Optional[str]): The status of the bridge.
    """

    ip: Optional[str]
    name: str
    type: str
    interfaces: List[Interface]
    status: Optional[str]


class BridgeCreateResponse(BaseModel):
    """Schema for the response after creating a bridge.

    Attributes:
        id (str): The unique identifier of the bridge.
        ip (str): The IP address of the bridge.
        name (str): The name of the bridge.
        gateway (str): The gateway IP address of the bridge.
        power_state (str): The power state of the bridge.
        mac (str): The MAC address of the bridge.
        netmask (Optional[str]): The netmask of the bridge.
        inf_type (str): The type of the bridge.
        status (str): The status of the bridge.
        interface_extra_specs (InterfaceExtraSpecs): Additional specifications
            for the bridge's interface.
    """

    id: str
    ip: str
    name: str
    gateway: str
    power_state: str
    mac: str
    netmask: Optional[str]
    inf_type: str
    status: str
    interface_extra_specs: InterfaceExtraSpecs


class ListOfInterfaces(BaseModel):
    """Schema for a list of network interfaces.

    Attributes:
        interfaces (List[Optional[Interface]]): A list of network interfaces.
    """

    interfaces: List[Optional[Interface]]
