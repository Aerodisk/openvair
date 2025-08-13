"""DTOs for external command operations in the image module.

This module defines command objects used to send event-related actions
from the image module to other services or subsystems.
"""

from uuid import UUID

from openvair.common.base_pydantic_models import BaseDTOModel


class AddEventCommandDTO(BaseDTOModel):
    """DTO for adding an event related to an image entity.

    Contains metadata required to register an event in the system from
    the image module.

    Attributes:
        object_id (UUID): Unique identifier of the related object (e.g., image).
        user_id (UUID): Unique identifier of the user who triggered the event.
        event (str): Name or type of the event.
        information (str): Additional descriptive information about the event.
    """

    object_id: UUID
    user_id: UUID
    event: str
    information: str
