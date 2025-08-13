"""Contract definitions for interacting with the Event Store service layer.

This module contains data models (contracts) that define the expected structure
and validation rules for messages sent to the Event Store service over the
messaging layer. These contracts are used for inter-module communication and
must remain stable to ensure compatibility between the Event Store and its
consumers.

Classes:
    CreateEventServiceCommand: Command object representing the required
        information to record a new event in the Event Store service.

Notes:
    - These models serve as public contracts and should be versioned carefully.
    - Any breaking changes require coordinated updates across all dependent
      modules and services.
"""

from uuid import UUID

from openvair.common.base_pydantic_models import BaseDTOModel


class CreateEventServiceCommand(BaseDTOModel):
    """Command contract for creating a new event in the Event Store service.

    This model defines the required fields and validation rules for sending a
    "create event" command to the Event Store service layer via the messaging
    system. It is used in inter-module communication and serves as part of the
    public contract between the Event Store and its consumers.

    Attributes:
        module (str): Name of the module where the event originated.
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


class GetLastEventsServiceCommand(BaseDTOModel):
    """Command contract for retrieving recent events from the Event Store.

    This model defines the required parameter(s) for requesting a limited set of
    the latest events from the Event Store service layer. It is used in
    inter-module communication over the messaging system and ensures consistent
    request formatting.

    Attributes:
        limit (int): The maximum number of recent events to retrieve.
    """

    limit: int


class GetEventsByModuleServiceCommand(BaseDTOModel):
    """Command contract for retrieving events by originating module.

    This model specifies the parameter(s) required to fetch events that were
    recorded by a specific module in the system. It is part of the public
    messaging contract and must remain backward compatible.

    Attributes:
        module_name (str): The name of the originating module whose events
            should be retrieved.
    """

    module_name: str
