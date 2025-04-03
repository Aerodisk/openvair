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
from openvair.libs.messaging.exceptions import RpcException
from openvair.modules.template.adapters.dto import (
    TemplateCreateCommandDTO,
)
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.template.adapters.serializer import TemplateSerializer
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
    def create_template(self, data: Dict) -> Dict:  # noqa: D102
        dto = TemplateCreateCommandDTO.model_validate(data)
        volume_id = dto.base_volume_id
        template_data = dto.template

        # Перед запись инфо о шаблоне, получаем базовый том и хранилище, если их нет, то поднимается ошибка  # noqa: E501, RUF003, W505
        ## проверка наличия базового тома
        try:
            _ = self.volume_service_client.get_volume({'volume_id': volume_id})
        except RpcException:
            LOG.error(f'Error while getting base volume with id: {volume_id}')
            raise Exception  # noqa: TRY002

        ## проверка существования storage
        try:
            _ = self.storage_service_client.get_storage(
                {'storage_id': template_data.storage_id}
            )
        except RpcException:
            LOG.error(
                'Error while getting base storage with id: '
                f'{template_data.storage_id}'
            )
            raise Exception  # noqa: TRY002

        orm_template = TemplateSerializer.to_orm(template_data)

        with self.uow as uow:
            # TODO нужно сделать статус
            uow.templates.add(orm_template)
            uow.commit()

        result = self.domain_rpc.call(
            'create',
            data_for_manager=TemplateSerializer.to_dto(
                orm_template
            ).model_dump(),
        )

        orm_template = TemplateSerializer.from_dict(result)
        with self.uow as uow:
            # TODO нужно сделать статус
            uow.templates.update(orm_template)
            uow.commit()

        return TemplateSerializer.to_dto(orm_template).model_dump(mode='json')

    def update_template(self) -> None:  # noqa: D102
        ...
    def delete_template(self) -> None:  # noqa: D102
        ...
    def create_volume_from_template(self) -> None:  # noqa: D102
        ...
