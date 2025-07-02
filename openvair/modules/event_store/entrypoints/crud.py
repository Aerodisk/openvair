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
from openvair.libs.validation.validators import Validator
from openvair.modules.event_store.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.entrypoints import schemas
from openvair.modules.event_store.service_layer import unit_of_work2
from openvair.modules.event_store.adapters.serializer import DataSerializer
from openvair.modules.event_store.service_layer.services import (
    EventstoreServiceLayerManager,
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
        self.uow = unit_of_work2.EventstoreSqlAlchemyUnitOfWork
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def new_get_all_events(self) -> List:
        """Retrieve all events from the database.

        This method retrieves all events from the database, serializes them
        to web format, validates them against the Event schema, and returns
        them in a paginated format.

        Returns:
            Page[schemas.Event]: A paginated list of all events.
        """
        LOG.info('Call service layer on getting events.')

        events: List = self.service_layer_rpc.call(
            EventstoreServiceLayerManager.get_all_events.__name__,
            data_for_method={},
        )
        LOG.info('after service layer')

        return Validator.validate_objects(events, schemas.Event)

    def new_get_all_events_by_module(self) -> List:
        """Retrieve all events by module from the database.

        This method retrieves all events for a specific module from the
        database, serializes them to web format, validates them against the
        Event schema, and returns them in a paginated format.

        Returns:
            Page[schemas.Event]: A paginated list of events filtered by module.
        """
        LOG.info('Call service layer on getting events by module.')
        events: List = self.service_layer_rpc.call(
            EventstoreServiceLayerManager.get_all_events_by_module.__name__,
            data_for_method={'module_name': self.module_name},
        )

        return Validator.validate_objects(events, schemas.Event)

    def new_get_last_events(self, limit: int) -> List:
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
        events: List = self.service_layer_rpc.call(
            EventstoreServiceLayerManager.get_last_events.__name__,
            data_for_method={'limit': limit},
        )

        return Validator.validate_objects(events, schemas.Event)

    def new_add_event(
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

            data = event_info._asdict()
            data['user_id'] = str(data['user_id'])
            self.service_layer_rpc.call(
                EventstoreServiceLayerManager.add_event.__name__,
                data_for_method=data,
            )
            LOG.info('Event info was successfully added')
        except Exception as e:
            LOG.exception('An error occurred')
            LOG.debug(e)

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
            with self.uow() as uow:
                db_event = DataSerializer.to_db(event_info._asdict())
                uow.events.add(db_event)
                uow.commit()
            LOG.info('Event info was successfully added')
        except Exception as e:
            LOG.exception('An error occurred')
            LOG.debug(e)
