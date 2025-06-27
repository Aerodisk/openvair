"""Some description"""

from typing import Dict, List

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.event_store.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient

# from openvair.modules.event_store.service_layer import unit_of_work
from openvair.modules.event_store.service_layer import unit_of_work2
from openvair.modules.event_store.adapters.serializer import DataSerializer

LOG = get_logger(__name__)


class EventstoreServiceLayerManager(BackgroundTasks):
   """Some description"""
   def __init__(self) -> None:
      """Some description"""
      super().__init__()
      # self.uow = unit_of_work.SqlAlchemyUnitOfWork()
      self.uow = unit_of_work2.EventstoreSqlAlchemyUnitOfWork()
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

   def get_all_events_by_module(self, data: Dict) -> List:
      """Some description"""
      LOG.info(f'Getting events by module {data["module_name"]}, service layer')
      with self.uow:
         return [
             DataSerializer.to_web(event)
             for event in self.uow.events.get_all_by_module(data['module_name'])
         ]

   def get_last_events(self, data: Dict) -> List:
      """Some description"""
      LOG.info('Getting last events, service layer')
      with self.uow:
         return [
             DataSerializer.to_web(event)
             for event in self.uow.events.get_last_events(data['limit'])
         ]

   def add_event(self, data: Dict) -> None:
      """Some description"""
      LOG.info('Adding event, service layer')
      with self.uow:
         db_event = DataSerializer.to_db(data)
         self.uow.events.add(db_event)
         self.uow.commit()
