"""DTOs for internal service-layer command operations in the event store module.

This module defines command objects used to trigger service and domain-level
event creation within the system.
"""

from uuid import UUID

from openvair.common.base_pydantic_models import BaseDTOModel


class CreateEventServiceCommandDTO(BaseDTOModel):
    """DTO for creating an event at the service layer.

    Contains the required metadata to record a new event in the system.

    Attributes:
        module (str): Name of the module where the event originated.
        object_id (UUID): Unique identifier of the affected object.
        user_id (UUID): Unique identifier of the user who triggered the event.
        event (str): Name or type of the event.
        information (str): Additional details about the event.
    """

    module: str
    object_id: UUID
    user_id: UUID
    event: str
    information: str
