"""Module for event CRUD operations.

This module defines the `EventCrud` class, which handles various CRUD operations
related to events, including retrieving all events, retrieving events by module,
retrieving the last N events, and adding a new event. It utilizes the
`DataSerializer` class for data serialization and the `SqlAlchemyUnitOfWork`
for database transactions.

Classes:
    EventCrud: Class for managing CRUD operations on events.
"""

import uuid
from typing import List
from collections import namedtuple

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import validate_objects
from openvair.modules.event_store.entrypoints import schemas, unit_of_work
from openvair.modules.event_store.adapters.serializer import DataSerializer

LOG = get_logger(__name__)

CreateEventInfo = namedtuple(
    'CreateEventInfo',
    ['module', 'object_id', 'user_id', 'event', 'information'],
)


class EventCrud:
    """Class for managing CRUD operations on events."""

    def __init__(self, module_name: str = 'event-store'):
        """Initialize the EventCrud instance.

        Args:
            module_name (str): Name of the module. Defaults to 'event-store'.
        """
        self.module_name = module_name
        self.uow = unit_of_work.SqlAlchemyUnitOfWork()

    def get_all_events(self) -> List:
        """Retrieve all events from the database.

        This method retrieves all events from the database, serializes them
        to web format, validates them against the Event schema, and returns
        them in a paginated format.

        Returns:
            Page[schemas.Event]: A paginated list of all events.
        """
        with self.uow:
            web_events = [
                DataSerializer.to_web(event)
                for event in self.uow.events.get_all()
            ]
            return validate_objects(web_events, schemas.Event)

    def get_all_events_by_module(self) -> List:
        """Retrieve all events by module from the database.

        This method retrieves all events for a specific module from the
        database, serializes them to web format, validates them against the
        Event schema, and returns them in a paginated format.

        Returns:
            Page[schemas.Event]: A paginated list of events filtered by module.
        """
        with self.uow:
            web_events = [
                DataSerializer.to_web(event)
                for event in self.uow.events.get_all_by_module(self.module_name)
            ]
            return validate_objects(web_events, schemas.Event)

    def get_last_events(self, limit: int = 25) -> List:
        """Retrieve the last N events from the database.

        This method retrieves the last N events from the database, serializes
        them to web format, validates them against the Event schema, and returns
        them in a paginated format.

        Args:
            limit (int): The number of events to retrieve. Defaults to 25.

        Returns:
            Page[schemas.Event]: A paginated list of the last N events.
        """
        with self.uow:
            web_events = [
                DataSerializer.to_web(event)
                for event in self.uow.events.get_last_events(limit)
            ]
            return validate_objects(web_events, schemas.Event)

    def add_event(
        self,
        object_id: str,
        user_id: str,
        event: str,
        information: str,
    ) -> None:
        """Add a new event to the database.

        This method creates a new event from the provided information,
        serializes it to database format, and adds it to the database. It also
        commits the transaction.

        Args:
            object_id (str): The ID of the related object.
            user_id (str): The ID of the user creating the event.
            event (str): The event description.
            information (str): Additional information about the event.

        Raises:
            Exception: If an error occurs during the event creation or database
                transaction.
        """
        try:
            LOG.info('Starting add event')
            event_info = CreateEventInfo(
                module=self.module_name,
                object_id=object_id,
                user_id=uuid.UUID(user_id),
                event=event,
                information=information,
            )
            LOG.info(f'Event info: {event_info}')
            with self.uow:
                db_event = DataSerializer.to_db(event_info._asdict())
                self.uow.events.add(db_event)
                self.uow.commit()
            LOG.info('Event info was successfully added')
        except Exception as e:
            LOG.exception('An error occurred')
            LOG.debug(e)
