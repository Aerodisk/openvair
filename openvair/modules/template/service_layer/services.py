"""Service layer manager for template processing.

This module defines the TemplateServiceLayerManager, which handles service-level
operations such as database transactions and messaging.

Classes:
    - TemplateServiceLayerManager: Manager handling template service logic.

Dependencies:
    - MessagingClient: Handles message-based communication.
    - TemplateSqlAlchemyUnitOfWork: Unit of Work for template operations.
    - EventCrud: Manages event store interactions.
"""

from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.template.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)

# from openvair.libs.messaging.exceptions import RpcException
# from openvair.modules.template.adapters.orm import Template as TemplateORM
from openvair.libs.messaging.messaging_agents import MessagingClient

# from openvair.modules.template.service_layer.dtos import TemplateDTO
from openvair.modules.event_store.entrypoints.crud import EventCrud

# from openvair.modules.template.adapters.serializer import TemplateSerializer
from openvair.modules.template.service_layer.unit_of_work import (
    TemplateSqlAlchemyUnitOfWork,
)
from openvair.libs.messaging.clients.rpc_clients.volume_rpc_client import (
    VolumeServiceLayerRPCClient,
)
from openvair.libs.messaging.clients.rpc_clients.storage_rpc_client import (
    StorageServiceLayerRPCClient,
)

LOG = get_logger(__name__)


class TemplateServiceLayerManager(BackgroundTasks):
    """Manager for handling template service operations.

    This class handles database interactions, messaging, and event logging.

    Attributes:
        uow (TemplateSqlAlchemyUnitOfWork): Unit of Work for template
            transactions.
        domain_rpc (MessagingClient): RPC client for domain layer communication.
        service_layer_rpc (MessagingClient): RPC client for service layer
            communication.
        event_store (EventCrud): Event store manager for templates.
    """

    def __init__(self) -> None:
        """Initializes the service layer manager.

        Sets up the Unit of Work, messaging clients, and event store.
        """
        super().__init__()
        self.uow = TemplateSqlAlchemyUnitOfWork()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )
        self.volume_service_client = VolumeServiceLayerRPCClient()
        self.storage_service_client = StorageServiceLayerRPCClient()
        self.event_store = EventCrud('templates')

    def get_all_templates(self) -> None:  # noqa: D102
        ...
    def get_template(self) -> None:  # noqa: D102
        ...
    def create_template(self, data: Dict) -> None:  # noqa: D102
        # orm_template: TemplateORM = TemplateSerializer.from_dict(data)
        # dto_template: TemplateDTO = TemplateSerializer.to_dto(orm_template)

        # # #Перед запись инфо о шаблоне, получаем базовый том и хранилище, если их нет, то поднимается ошибка  # noqa: E501, RUF003, W505
        # # ## проверка наличия базового тома
        # try:
        #     base_volume = self.volume_service_client.get_volume({'volume_id': orm_template.base_volume_id})  # noqa: E501, W505
        # except RpcException as err:
        #     LOG.error(f'Error while getting base volume with id: {orm_template.base_volume_id}')  # noqa: E501, W505
        #     raise Exception

        # ## проверка существования storage
        # try:
        #     storgae = self.storage_service_client.get_storage({'storage_id': template_data.storage_id})  # noqa: E501, W505
        # except RpcException as err:
        #     LOG.error(f'Error while getting base storage with id: {template_data.storage_id}')  # noqa: E501, W505
        #     raise ServiceLayelEx

        # with self.uow as uow:
        #     db_tmp = DataSerializer.to_db(template_data.model_dump())
        #     db_tmp.status =
        #     uow.templates.add(db_tmp)

        ...

    def update_template(self) -> None:  # noqa: D102
        ...
    def delete_template(self) -> None:  # noqa: D102
        ...
    def create_volume_from_template(self) -> None:  # noqa: D102
        ...
