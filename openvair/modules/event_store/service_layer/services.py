"""Some description"""

from typing import List

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.event_store.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.service_layer import unit_of_work
from openvair.modules.event_store.adapters.serializer import DataSerializer

LOG = get_logger(__name__)


class EventstoreServiceLayerManager(BackgroundTasks):
   """Some description"""
   def __init__(self) -> None:
      """Some description"""
      super().__init__()
      self.uow = unit_of_work.SqlAlchemyUnitOfWork()
      self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
      )

   def get_all_events(self) -> List:
      """Some description"""
      LOG.info('Getting events, service layer')
      with self.uow:
         return [
             DataSerializer.to_web(event)
             for event in self.uow.events.get_all()
         ]
         # return web_events
