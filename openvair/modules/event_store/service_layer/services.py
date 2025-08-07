"""Service layer manager for event processing.

This module defines the EventstoreServiceLayerManager, which handles
service-level operations such as database transactions and messaging.

Classes:
    - EventstoreServiceLayerManager: Manager handling event service logic.

Dependencies:
    - MessagingClient: Handles message-based communication.
    - EventStoreSqlAlchemyUnitOfWork: Unit of Work for event operations.
"""

from typing import Dict, List

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.event_store.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.service_layer import unit_of_work
from openvair.modules.event_store.adapters.serializer import (
    DataSerializer,
    CreateSerializer,
)
from openvair.modules.event_store.adapters.dto.internal.models import (
    CreateEventModelDTO,
)
from openvair.modules.event_store.adapters.dto.internal.commands import (
    CreateEventServiceCommandDTO,
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
                DataSerializer.to_web(event) for event in uow.events.get_all()
            ]

    def get_all_events_by_module(self, data: Dict) -> List:
        """Retrieve all events by module from the database.

        Returns:
           List: A list of serialized event representations.
        """
        LOG.info(
            f'Getting events by module {data["module_name"]}, service layer'
        )
        with self.uow() as uow:
            return [
                DataSerializer.to_web(event)
                for event in uow.events.get_all_by_module(data['module_name'])
            ]

    def get_last_events(self, data: Dict) -> List:
        """Retrieve a sertain number of last events from the database.

        Returns:
           List: A list of serialized event representations.
        """
        LOG.info('Getting last events, service layer')
        with self.uow() as uow:
            return [
                DataSerializer.to_web(event)
                for event in uow.events.get_last_events(data['limit'])
            ]

    def add_event(self, creating_data: Dict) -> None:
        """Create a new event, persist it in the db, start async creation.

        Args:
           creating_data (Dict): A dictionary with event creation fields.

        Returns:
           None
        """
        LOG.info('Adding event, service layer')
        creating_command = CreateEventServiceCommandDTO.model_validate(
            creating_data
        )
        db_event = CreateSerializer.to_orm(
            CreateEventModelDTO.model_validate(creating_command)
        )
        with self.uow() as uow:
            uow.events.add(db_event)
            uow.commit()
        LOG.info('Event successfully added')
