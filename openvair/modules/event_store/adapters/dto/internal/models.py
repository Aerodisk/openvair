"""DTOs for internal data structures in the event store module.

Includes models used to transfer event data between API, domain and service
layers.
"""

from uuid import UUID

from openvair.common.pydantic_types import UTCDateTime
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


class ApiEventModelDTO(BaseDTOModel):
    """DTO used to represent an event in the API layer.

    Attributes:
        id (int): Unique identifier of the event.
        module (str): Name of the module where the event occurred.
        object_id (UUID): Unique identifier of the related object.
        user_id (UUID): Unique identifier of the user who triggered the event.
        event (str): Name or type of the event.
        timestamp (datetime): Time when the event was recorded.
        information (str): Additional context or metadata about the event.
    """

    id: int
    module: str
    object_id: UUID
    user_id: UUID
    event: str
    timestamp: UTCDateTime
    information: str
