"""Schemas for virtual network API requests and responses.

This module defines the data schemas used for validating and serializing
data in the virtual network API. These schemas are used for creating,
retrieving, and manipulating virtual network configurations and their
associated port groups.

Classes:
    PortGroup: Represents a port group configuration.
    VirtualNetwork: Represents a virtual network configuration.
    VirtualNetworkResponse: Represents a response containing information about a
        virtual network.
    ListOfVirtualNetworksResponse: Represents a response containing a list of
        virtual networks.
    ErrorResponseModel: Represents an error response.
"""

from typing import List, Type, Union, Literal

from pydantic import (
    Field,
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)
from pydantic.types import UUID4
from typing_extensions import Self


class PortGroup(BaseModel):
    """Represents a port group configuration.

    Attributes:
        port_group_name (str): The name of the port group.
        is_trunk (str): Indicates if the port group is a trunk ('yes' or 'no').
        tags (List[str]): List of VLAN tags associated with the port group.
    """

    port_group_name: str = 'trunk_port_group'
    is_trunk: Literal['yes', 'no']
    tags: List[Union[int, str]] = Field(
        ..., examples=[['10', '20', '30', '40']]
    )
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_tags_and_is_trunk(self) -> Self:
        """Validates that if `tags` has more than one tag, and `is_trunk` state.

        Args:
            values (Dict): The dictionary of field values to validate.

        Returns:
            Dict: The validated values.

        Raises:
            ValueError: If `tags` has more than one element and `is_trunk` is
                not 'yes'.
        """
        # tags = values.get('tags')
        # is_trunk = values.get('is_trunk')

        # It will be return input dict withoth needed value and then pydantic
        # raise standart pydantic validation error for fields
        if not self.tags or not self.is_trunk:
            return self

        if len(self.tags) > 1 and self.is_trunk != 'yes':
            message = (
                'If tags contains more than one tag, '
                'must be turn on trunk mode.'
            )
            raise ValueError(message)

        return self


class VirtualNetwork(BaseModel):
    """Represents a virtual network configuration.

    Attributes:
        network_name (str): The name of the virtual network.
        forward_mode (str): The forwarding mode of the virtual network.
        bridge (str): The bridge associated with the virtual network.
        virtual_port_type (str): The type of virtual port used by the virtual
            network.
        port_groups (List[PortGroup]): List of port groups associated with the
            virtual network.
    """

    network_name: str = 'my_virtual_network'
    forward_mode: str = 'bridge'
    bridge: str = 'my_bridge'
    virtual_port_type: str = 'openvswitch'
    port_groups: List[PortGroup]

    @classmethod
    @field_validator('port_groups')
    @classmethod
    def port_groups_validator(cls, value: List) -> List:
        """Validates that the `port_groups` attribute is not empty or None.

        Args:
            value (List): The value to validate.

        Returns:
            List: The validated value.

        Raises:
            ValueError: If the value is empty or None.
        """
        if not value:
            msg = 'port_groups cannot be empty or None'
            raise ValueError(msg)
        return value

    @classmethod
    @field_validator('bridge')
    @classmethod
    def bridge_validator(cls, value: str) -> str:
        """Validates that the `bridge` attribute is not 'virbr0'.

        Args:
            value (str): The value to validate.

        Returns:
            str: The validated value.

        Raises:
            ValueError: If the value is 'virbr0'.
        """
        if value == 'virbr0':
            msg = 'bridge virbr0 is NAT bridge and cannot have a port group'
            raise ValueError(msg)
        return value


class VirtualNetworkResponse(VirtualNetwork):
    """Represents a response containing information about a virtual network.

    Attributes:
        id (UUID4): The ID of the virtual network.
        state (str): The state of the virtual network.
        autostart (str): Indicates if the virtual network should start
            automatically.
        persistent (str): Indicates if the virtual network configuration is
            persistent.
        virsh_xml (str): The virsh XML configuration of the virtual network.
    """

    id: UUID4
    state: str
    autostart: str
    persistent: str
    virsh_xml: str
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj: Type[VirtualNetwork]) -> Self:
        """Creates a VirtualNetworkResponse object from an ORM object.

        Args:
            obj: The ORM object representing the virtual network.

        Returns:
            VirtualNetworkResponse: An instance of VirtualNetworkResponse.
        """
        # Adds a class method to convert port_groups to a list of dictionaries
        return cls(
            **{
                **obj.__dict__,
                'port_groups': [
                    PortGroup.from_orm(pg) for pg in obj.port_groups
                ],
            }
        )


class ListOfVirtualNetworksResponse(BaseModel):
    """Represents a response containing a list of virtual networks.

    Attributes:
        virtual_networks (List[VirtualNetworkResponse]): List of virtual
            networks.
    """

    virtual_networks: List[VirtualNetworkResponse]


class ErrorResponseModel(BaseModel):
    """Represents an error response.

    Attributes:
        details (str): Details of the error.
    """

    details: str
