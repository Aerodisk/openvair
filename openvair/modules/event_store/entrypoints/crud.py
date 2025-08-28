"""Module for event CRUD operations.

This module defines the `EventCrud` class, which handles various CRUD operations
related to events, including retrieving all events, retrieving events by module,
retrieving the last N events, and adding a new event. It utilizes the
`DataSerializer` class for data serialization and the `SqlAlchemyUnitOfWork`
for database transactions.

Classes:
    EventCrud: Class for managing CRUD operations on events.
"""

from uuid import UUID
from typing import List
from collections import namedtuple

from openvair.libs.log import get_logger
from openvair.libs.validation.validators import Validator
from openvair.modules.event_store.entrypoints import schemas
from openvair.modules.event_store.service_layer import unit_of_work
from openvair.modules.event_store.adapters.serializer import DataSerializer
from openvair.modules.event_store.entrypoints.schemas import Event
from openvair.libs.messaging.clients.rpc_clients.event_store_rpc_client import (
    EventStoreServiceLayerRPCClient,
)

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
        self.uow = unit_of_work.EventStoreSqlAlchemyUnitOfWork
        self.service_layer_rpc_client = self.event_client = (
            EventStoreServiceLayerRPCClient(module_name)
        )

    def new_get_all_events(self) -> List[Event]:
        """Retrieve all events from the database.

        This method retrieves all events from the database, serializes them
        to web format, validates them against the Event schema, and returns
        them in a paginated format.

        Returns:
            Page[schemas.Event]: A paginated list of all events.
        """
        LOG.info('Call service layer on getting events.')
        events: List = self.service_layer_rpc_client.get_all_events()
        return Validator.validate_objects(events, schemas.Event)

    def new_get_all_events_by_module(self) -> List[Event]:
        """Retrieve all events by module from the database.

        This method retrieves all events for a specific module from the
        database, serializes them to web format, validates them against the
        Event schema, and returns them in a paginated format.

        Returns:
            Page[schemas.Event]: A paginated list of events filtered by module.
        """
        LOG.info('Call service layer on getting events by module.')
        events: List = self.service_layer_rpc_client.get_all_events_by_module()
        return Validator.validate_objects(events, schemas.Event)

    def new_get_last_events(self, limit: int) -> List[Event]:
        """Retrieve the last N events from the database.

        This method retrieves the last N events from the database, serializes
        them to web format, validates them against the Event schema,
        and returns them in a paginated format.

        Args:
            limit (int): The number of events to retrieve. Defaults to 25.

        Returns:
            Page[schemas.Event]: A paginated list of the last N events.
        """
        LOG.info('Call service layer on getting events by module.')
        events: List = self.service_layer_rpc_client.get_last_events(
            limit=limit,
        )

        return Validator.validate_objects(events, schemas.Event)

    def new_add_event(
        self,
        object_id: UUID,
        user_id: UUID,
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
        LOG.info('Starting add event')
        self.service_layer_rpc_client.add_event(
            object_id=object_id,
            user_id=user_id,
            event=event,
            information=information,
        )
        LOG.info('Event info was successfully added')

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
            try:
                user_uuid = UUID(user_id)
            except (ValueError, TypeError):
                LOG.warning(
                    f'Invalid user_id for event: {user_id!r}. '
                    f'Setting user_id to None.'
                )
                user_uuid = None
            event_info = CreateEventInfo(
                module=self.module_name,
                object_id=object_id,
                user_id=user_uuid,
                event=event,
                information=information,
            )
            LOG.info(f'Event info: {event_info}')
            with self.uow() as uow:
                db_event = DataSerializer.to_db(event_info._asdict())
                uow.events.add(db_event)
                uow.commit()
            LOG.info('Event info was successfully added')
        except Exception as e:
            LOG.exception('An error occurred')
            LOG.debug(e)
