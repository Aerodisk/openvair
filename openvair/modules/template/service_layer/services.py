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

from uuid import UUID
from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.template.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.libs.messaging.exceptions import RpcException
from openvair.modules.template.adapters.dto import (
    VolumeQuery,
    StorageQuery,
    TemplateCreateCommandDTO,
)
from openvair.modules.template.adapters.orm import Template
from openvair.modules.template.shared.enums import TemplateStatus
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.template.adapters.serializer import TemplateSerializer
from openvair.modules.template.service_layer.exceptions import (
    VolumeRetrievalException,
    StorageRetrievalException,
)
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
        self._check_volume_exist(volume_id)
        self._check_storage_exist(template_data.storage_id)

        orm_template = TemplateSerializer.to_orm(template_data)
        with self.uow as uow:
            uow.templates.add(orm_template)
            uow.commit()

        self._update_and_log_event(
            orm_template, TemplateStatus.NEW, 'TemplateCreationPrepared'
        )
        self._create_template(
            TemplateSerializer.to_dto(orm_template).model_dump(mode='json'),
        )
        # self.service_layer_rpc.cast(
        #     self._create_template.__name__,
        #     data_for_method=TemplateSerializer.to_dto(
        #         orm_template
        #     ).model_dump(mode='json'),
        # )
        return TemplateSerializer.to_dto(orm_template).model_dump(mode='json')

    def update_template(self) -> None:  # noqa: D102
        ...
    def delete_template(self) -> None:  # noqa: D102
        ...
    def create_volume_from_template(self) -> None:  # noqa: D102
        ...

    def _create_template(self, data: Dict) -> None:
        LOG.info('2')
        orm_template = TemplateSerializer.from_dict(data)
        self._update_and_log_event(
            orm_template, TemplateStatus.CREATING, 'TemplateCreationStarted'
        )
        LOG.info('1')
        try:
            result = self.domain_rpc.call('create', data_for_manager=data)
            LOG.info('2')
        except RpcException as err:
            self._update_and_log_event(
                orm_template,
                TemplateStatus.ERROR,
                'TemplateCreationFailed',
                str(err),
            )
            LOG.error('Error while creating template', exc_info=True)
            return

        # TODO согласовать сериализацию и возвращаемый результат, когда будет известен  # noqa: E501, W505
        orm_template = TemplateSerializer.from_dict(result)
        self._update_and_log_event(
            orm_template, TemplateStatus.AVAILABLE, 'TemplateCreated'
        )

    def _update_and_log_event(
        self,
        orm_template: Template,
        status: TemplateStatus,
        event_type: str,
        message: str = '',
    ) -> None:
        orm_template.status = status
        orm_template.information = message
        with self.uow as uow:
            uow.templates.update(orm_template)
            uow.commit()

        # TODO типизировать event
        event = {
            'object_id': str(orm_template.id),
            'user_id': str(uuid.uuid4()),  # TODO предавать user_id
            'event': event_type,
            'information': f'Status: {status.value}. message: {message}',
            # 'status': status.value, # TODO передавать статус и убрать его из сообщения  # noqa: E501, RUF003, W505
        }
        self.event_store.add_event(**event)

    def _check_volume_exist(self, volume_id: UUID) -> None:
        volume_query_payload = VolumeQuery(volume_id=volume_id).model_dump(
            mode='json'
        )
        try:
            self.volume_service_client.get_volume(volume_query_payload)
        except RpcException as rpc_volume_err:
            LOG.error(
                f'Error while getting base volume with id: {volume_id}',
                exc_info=True,
            )
            message = f'Failed to get volume with id {volume_id}'
            raise VolumeRetrievalException(message) from rpc_volume_err

    def _check_storage_exist(self, storage_id: UUID) -> None:
        storage_query_payload = StorageQuery(storage_id=storage_id).model_dump(
            mode='json'
        )
        try:
            self.storage_service_client.get_storage(storage_query_payload)
        except RpcException as rpc_storage_err:
            LOG.error(
                f'Error while getting base storage with id: ' f'{storage_id}',
                exc_info=True,
            )
            message = f'Failed to get storage with id {storage_id}'
            raise StorageRetrievalException(message) from rpc_storage_err


if __name__ == '__main__':
    import uuid
    from pathlib import Path

    from openvair.modules.template.adapters.dto import BaseTemplateDTO
    from openvair.modules.template.entrypoints.schemas import CreateTemplate

    data = CreateTemplate(
        name='tmp_name5',
        path=Path('/'),
        storage_id=uuid.UUID('0e08ef60-f09f-4ddd-90ba-4e556edd34b3'),
        is_backing=False,
        base_volume_id=uuid.UUID('b2e06ed2-179d-4470-a100-10332e7e7cfa'),
        description=None,
    )

    command = TemplateCreateCommandDTO(
        base_volume_id=data.base_volume_id,
        template=BaseTemplateDTO.model_validate(
            data.model_dump(exclude={'base_volume_id'})
        ),
    )

    serv = TemplateServiceLayerManager()

    serv.create_template(command.model_dump(mode='json'))
