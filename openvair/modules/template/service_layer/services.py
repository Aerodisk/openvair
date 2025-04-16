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

from uuid import UUID, uuid4
from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.template.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.libs.messaging.exceptions import RpcException
from openvair.modules.template.domain.base import BaseTemplate
from openvair.modules.template.adapters.orm import Template
from openvair.modules.template.shared.enums import TemplateStatus
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.template.adapters.serializer import (
    TemplateViewSerializer,
    TemplateCreateSerializer,
)
from openvair.modules.template.service_layer.exceptions import (
    VolumeRetrievalException,
    StorageRetrievalException,
)
from openvair.modules.template.service_layer.unit_of_work import (
    TemplateSqlAlchemyUnitOfWork,
)
from openvair.modules.template.adapters.dto.external.models import (
    GetVolumeDTO,
    GetStorageDTO,
)
from openvair.modules.template.adapters.dto.internal.models import (
    CreateTemplateDTO,
    DomainTemplateManagerDTO,
)
from openvair.modules.template.adapters.dto.external.commands import (
    GetVolumeCommandDTO,
    GetStorageCommandDTO,
)
from openvair.modules.template.adapters.dto.internal.commands import (
    EditTemplateServiceCommandDTO,
    CreateTemplateDomainCommandDTO,
    CreateTemplateServiceCommandDTO,
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

    # def get_all_templates(self) -> List:
    #     """Retrieves all template records from the database.

    #     Returns:
    #         List: A list of serialized templates in JSON-compatible format.
    #     """
    #     with self.uow as uow:
    #         orm_templates = uow.templates.get_all()
    #     return [
    #         TemplateSerializer.to_dto(template).model_dump(mode='json')
    #         for template in orm_templates
    #     ]

    # def get_template(self, getting_data: Dict) -> Dict:
    #     """Retrieves a single template by its ID.

    #     Args:
    #         getting_data (Dict): A dictionary containing the 'id' of the
    #             template.

    #     Returns:
    #         Dict: A JSON-serializable representation of the template.
    #     """
    #     dto = DTOGetTemplate.model_validate(getting_data)
    #     LOG.info(dto.id)
    #     with self.uow as uow:
    #         orm_template = uow.templates.get_or_fail(dto.id)
    #     return TemplateSerializer.to_dto(orm_template).model_dump(mode='json')

    def create_template(self, creating_data: Dict) -> Dict:  # noqa: D102
        input_dto = CreateTemplateServiceCommandDTO.model_validate(
            creating_data
        )

        # 2. Получаем volume и storage
        volume = self._get_volume_info(input_dto.base_volume_id)
        storage = self._get_storage_info(input_dto.storage_id)
        create_command_dto = CreateTemplateDTO(
            name=input_dto.name,
            description=input_dto.description,
            path=(
                storage.mount_point
                / f'template-{input_dto.name}.{volume.format}'
            ),
            tmp_format=volume.format,
            storage_id=input_dto.storage_id,
            is_backing=input_dto.is_backing,
            source_disk_path=volume.path / f'volume-{volume.id}',
        )
        orm = TemplateCreateSerializer.to_orm(create_command_dto)
        with self.uow as uow:
            uow.templates.add(orm)
            uow.commit()

        self._update_and_log_event(
            orm, TemplateStatus.NEW, 'TemplateCreationPrepared'
        )

        self.service_layer_rpc.cast(
            self._create_template.__name__,
            data_for_method={
                'id': str(orm.id),
                **create_command_dto.model_dump(mode='json'),
            },
        )

        return TemplateViewSerializer.to_dict(orm)

    def edit_template(self, updating_data: Dict) -> Dict:  # noqa: D102
        edit_command_dto = EditTemplateServiceCommandDTO.model_validate(
            updating_data
        )
        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(edit_command_dto.id)

        self._update_and_log_event(
            orm_template, TemplateStatus.EDITING, 'TemplateEditingStarted'
        )

        edit_data = TemplateViewSerializer.to_dict(orm_template)
        self.service_layer_rpc.cast(
            self._edit_template.__name__,
            data_for_method=edit_command_dto.model_dump(mode='json'),
        )
        return edit_data

    # def delete_template(self, deleting_data: Dict) -> Dict:
    #     dto = DTODeleteTemplate.model_validate(deleting_data)
    #     with self.uow as uow:
    #         orm_template = uow.templates.get_or_fail(dto.id)

    #     self._update_and_log_event(
    #         orm_template, TemplateStatus.DELETING, 'TemplateDeletingStarted'
    #     )

    #     delete_dto_data = TemplateSerializer.to_dict(orm_template)
    #     self.service_layer_rpc.cast(
    #         self._delete_template.__name__,
    #         data_for_method=delete_dto_data,
    #     )

    #     return TemplateSerializer.to_dict(orm_template)

    # def create_volume_from_template(
    #     self, volume_from_template_data: Dict
    # ) -> None:
    #     dto = DTOCreateVolumeFromTemplate.model_validate(
    #         volume_from_template_data
    #     )
    #     volume = dto.volume_info
    #     with self.uow as uow:
    #         orm_template = uow.templates.get_or_fail(dto.template_id)
    #     create_volume_data = DTOCreateVolume(
    #         name=volume.name,
    #         description=volume.description,
    #         storage_id=volume.storage_id,
    #         format=orm_template.tmp_format,
    #         size=orm_template.size,
    #         read_only=volume.read_only,
    #     )
    #     self.volume_service_client.create_volume(
    #         create_volume_data.model_dump(mode='json')
    #     )

    def _create_template(self, create_command_data: Dict) -> None:
        template_id = UUID(create_command_data.pop('id'))
        creation_dto = CreateTemplateDTO.model_validate(create_command_data)

        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(template_id)

        self._update_and_log_event(
            orm_template, TemplateStatus.CREATING, 'TemplateCreationStarted'
        )

        try:
            data_for_manager = DomainTemplateManagerDTO.model_validate(
                creation_dto
            )
            data_for_method = CreateTemplateDomainCommandDTO.model_validate(
                creation_dto
            )
            self.domain_rpc.call(
                BaseTemplate.create.__name__,
                data_for_manager=data_for_manager.model_dump(mode='json'),
                data_for_method=data_for_method.model_dump(mode='json'),
            )
            if creation_dto.name is not None:
                orm_template.name = creation_dto.name
            if creation_dto.description is not None:
                orm_template.description = creation_dto.description
        except RpcException as err:
            self._update_and_log_event(
                orm_template,
                TemplateStatus.ERROR,
                'TemplateCreationFailed',
                str(err),
            )
            LOG.error('Error while creating template', exc_info=True)
            return

        self._update_and_log_event(
            orm_template, TemplateStatus.AVAILABLE, 'TemplateCreated'
        )

    def _edit_template(self, edit_command_data: Dict) -> None:
        edit_dto = EditTemplateServiceCommandDTO.model_validate(
            edit_command_data
        )

        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(edit_dto.id)

        try:
            data_for_manager = DomainTemplateManagerDTO.model_validate(
                orm_template
            )
            data_for_method = EditTemplateServiceCommandDTO.model_validate(
                edit_command_data
            )
            self.domain_rpc.call(
                BaseTemplate.edit.__name__,
                data_for_manager=data_for_manager.model_dump(mode='json'),
                data_for_method=data_for_method.model_dump(mode='json'),
            )
            with self.uow as uow:
                if edit_dto.name is not None:
                    orm_template.name = edit_dto.name
                if edit_dto.description is not None:
                    orm_template.description = edit_dto.description
                uow.templates.update(orm_template)
                uow.commit()
        except RpcException as err:
            self._update_and_log_event(
                orm_template,
                TemplateStatus.ERROR,
                'TemplateEditingFaild',
                str(err),
            )
            LOG.error('Error while editing template', exc_info=True)
            return

        self._update_and_log_event(
            orm_template, TemplateStatus.AVAILABLE, 'TemplateEdited'
        )

    # def _delete_template(self, template_dto_data: Dict) -> None:
    #     orm_template = TemplateSerializer.from_dict(template_dto_data)
    #     try:
    #         LOG.info('')
    #         # result = self.domain_rpc.call('delete', template_dto_data)
    #     except RpcException as err:
    #         self._update_and_log_event(
    #             orm_template,
    #             TemplateStatus.ERROR,
    #             'TemplateDeletingFaild',
    #             str(err),
    #         )
    #         LOG.error('Error while deleting template', exc_info=True)
    #         return

    #     with self.uow as uow:
    #         uow.templates.delete(orm_template)
    #         uow.commit()

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
            'user_id': str(uuid4()),  # TODO предавать user_id
            'event': event_type,
            'information': f'Status: {status.value}. message: {message}',
            # 'status': status.value, # TODO передавать статус и убрать его из сообщения  # noqa: E501, RUF003, W505
        }
        self.event_store.add_event(**event)

    def _get_volume_info(self, volume_id: UUID) -> GetVolumeDTO:
        volume_query_payload = GetVolumeCommandDTO(
            volume_id=volume_id
        ).model_dump(mode='json')
        try:
            volume_data = self.volume_service_client.get_volume(
                volume_query_payload
            )
            return GetVolumeDTO.model_validate(volume_data)

        except RpcException as rpc_volume_err:
            LOG.error(
                f'Error while getting base volume with id: {volume_id}',
                exc_info=True,
            )
            message = f'Failed to get volume with id {volume_id}'
            raise VolumeRetrievalException(message) from rpc_volume_err

    def _get_storage_info(self, storage_id: UUID) -> GetStorageDTO:
        storage_query_payload = GetStorageCommandDTO(
            storage_id=storage_id
        ).model_dump(mode='json')
        try:
            storage_data = self.storage_service_client.get_storage(
                storage_query_payload
            )
            return GetStorageDTO.model_validate(storage_data)
        except RpcException as rpc_storage_err:
            LOG.error(
                f'Error while getting base storage with id: ' f'{storage_id}',
                exc_info=True,
            )
            message = f'Failed to get storage with id {storage_id}'
            raise StorageRetrievalException(message) from rpc_storage_err
