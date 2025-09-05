"""Service layer manager for event processing.

This module defines the EventstoreServiceLayerManager, which handles
service-level operations such as database transactions and messaging.

Classes:
    - EventstoreServiceLayerManager: Manager handling event service logic.

Dependencies:
    - MessagingClient: Handles message-based communication.
    - EventStoreSqlAlchemyUnitOfWork: Unit of Work for event operations.
"""

from typing import Any, Dict, List

from pydantic import validate_call

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.event_store.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.service_layer import unit_of_work
from openvair.libs.contracts.event_store_service import (
    CreateEventServiceCommand,
    GetLastEventsServiceCommand,
    GetEventsByModuleServiceCommand,
)
from openvair.modules.event_store.adapters.serializer import (
    ApiSerializer,
    CreateSerializer,
)
from openvair.modules.event_store.adapters.dto.internal.models import (
    CreateEventModelDTO,
)

LOG = get_logger(__name__)


class EventstoreServiceLayerManager(BackgroundTasks):
    """Manager for coordinating event operations in the service layer.

    This class orchestrates event-related tasks such as creation and
    get operations. It handles RPC communication and database transactions.

    Attributes:
       uow (EventStoreSqlAlchemyUnitOfWork): Unit of Work for event
          transactions.
       service_layer_rpc (MessagingClient): RPC client for internal task
          delegation.
    """

    def __init__(self) -> None:
        """Initialize the EventstoreServiceLayerManager.

        Sets up messaging client and unit of work.
        """
        super().__init__()
        self.uow = unit_of_work.EventStoreSqlAlchemyUnitOfWork
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_events(self) -> List:
        """Retrieve all events from the database.

        Returns:
           List: A list of serialized event representations.
        """
        LOG.info('Getting events, service layer')
        with self.uow() as uow:
            return [
                ApiSerializer.to_dict(event) for event in uow.events.get_all()
            ]

    def get_all_events_by_module(
        self,
        getting_data: Dict,
    ) -> List:
        """Retrieve all events by module from the database.

        Args:
            getting_data (Dict): Dict with module name
                for filtering

        Returns:
           List: A list of serialized event representations.
        """
        data = GetEventsByModuleServiceCommand(**getting_data)
        LOG.info(
            f'Getting events by module {data.module_name},'
            'service layer'
        )
        with self.uow() as uow:
            return [
                ApiSerializer.to_dict(event)
                for event in uow.events.get_all_by_module(
                    data.module_name
                )
            ]

    def get_last_events(
        self,
        getting_data: GetLastEventsServiceCommand,
    ) -> List[Dict[str, Any]]:
        """Retrieve a certain number of last events from the database.

        Args:
            getting_data (GetLastEventsServiceCommand): Object with limit num
                for getting

        Returns:
           List: A list of serialized event representations.
        """
        LOG.info('Getting last events, service layer')
        with self.uow() as uow:
            return [
                ApiSerializer.to_dict(event)
                for event in uow.events.get_last_events(getting_data.limit)
            ]

    @validate_call
    def add_event(self, creating_data: CreateEventServiceCommand) -> None:
        """Create a new event, persist it in the db, start async creation.

        Args:
           creating_data (CreateEventServiceCommand): Object with event data to
            add.

        Returns:
           None
        """
        LOG.info('Adding event, service layer')
        db_event = CreateSerializer.to_orm(
            CreateEventModelDTO.model_validate(creating_data)
        )
        with self.uow() as uow:
            uow.events.add(db_event)
            uow.commit()
        LOG.info('Event successfully added')
