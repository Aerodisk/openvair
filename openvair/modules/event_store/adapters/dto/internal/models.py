"""DTOs for internal data structures in the event store module.

Includes models used to transfer event data between API, domain and service
layers.
"""

from uuid import UUID

from openvair.common.base_pydantic_models import BaseDTOModel


class CreateEventModelDTO(BaseDTOModel):
    """DTO for creating a new event entry in the system.

    Attributes:
        module (str): Name of the module where the event occurred.
        object_id (UUID): Unique identifier of the affected object.
        user_id (UUID): Unique identifier of the user who triggered the event.
        event (str): Type or name of the event.
        information (str): Additional details or context about the event.
    """

    module: str
    object_id: UUID
    user_id: UUID
    event: str
    information: str
