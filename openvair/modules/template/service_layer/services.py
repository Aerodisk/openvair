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
from typing import Any, Dict, List, Optional

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
    ApiSerializer,
    CreateSerializer,
    DomainSerializer,
)
from openvair.modules.template.service_layer.exceptions import (
    VolumeRetrievalException,
    StorageRetrievalException,
)
from openvair.modules.template.service_layer.unit_of_work import (
    TemplateSqlAlchemyUnitOfWork,
)
from openvair.modules.template.adapters.dto.external.models import (
    VolumeModelDTO,
    StorageModelDTO,
)
from openvair.modules.template.adapters.dto.internal.models import (
    CreateTemplateModelDTO,
)
from openvair.modules.template.adapters.dto.external.commands import (
    GetVolumeCommandDTO,
    GetStorageCommandDTO,
)
from openvair.modules.template.adapters.dto.internal.commands import (
    EditTemplateDomainCommandDTO,
    GetTemplateServiceCommandDTO,
    EditTemplateServiceCommandDTO,
    CreateTemplateDomainCommandDTO,
    CreateTemplateServiceCommandDTO,
    DeleteTemplateServiceCommandDTO,
    AsyncCreateTemplateServiceCommandDTO,
)
from openvair.libs.messaging.clients.rpc_clients.volume_rpc_client import (
    VolumeServiceLayerRPCClient,
)
from openvair.libs.messaging.clients.rpc_clients.storage_rpc_client import (
    StorageServiceLayerRPCClient,
)

LOG = get_logger(__name__)


class TemplateServiceLayerManager(BackgroundTasks):
    """Manager for coordinating template operations in the service layer.

    This class orchestrates template-related tasks such as creation,
    updating, and deletion. It handles RPC communication, database transactions,
    domain delegation, and event logging.

    Attributes:
        uow (TemplateSqlAlchemyUnitOfWork): Unit of Work for template
            transactions.
        domain_rpc (MessagingClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (MessagingClient): RPC client for internal task
            delegation.
        volume_service_client (VolumeServiceLayerRPCClient): RPC client for
            volume queries.
        storage_service_client (StorageServiceLayerRPCClient): RPC client for
            storage queries.
        event_store (EventCrud): Event logger for template operations.
    """

    def __init__(self) -> None:
        """Initialize the TemplateServiceLayerManager.

        Sets up messaging clients, unit of work, and RPC clients for
        volume and storage services.
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

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Retrieve all templates from the database.

        Returns:
            List[Dict[str, Any]]: A list of serialized template representations.
        """
        LOG.info('Service layer handle request on getting templates')

        with self.uow as uow:
            orm_templates = uow.templates.get_all()

        api_templates: List[Dict[str, Any]] = [
            ApiSerializer.to_dict(orm_template)
            for orm_template in orm_templates
        ]

        LOG.info(
            'Service layer request on getting templates '
            'was successfully processed'
        )
        return api_templates

    def get_template(self, getting_data: Dict) -> Dict:
        """Retrieve a single template by its ID.

        Args:
            getting_data (Dict): A dictionary with the 'id' of the template.

        Returns:
            Dict: A serialized representation of the retrieved template.
        """
        LOG.info('Service layer handle request on getting template')

        getting_command = GetTemplateServiceCommandDTO.model_validate(
            getting_data
        )
        template_id = getting_command.id
        LOG.info(f'template_id: {template_id}')

        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(template_id)

        api_template: Dict[str, Any] = ApiSerializer.to_dict(orm_template)

        LOG.info(
            f'Service layer request on getting template {template_id} '
            'was successfully processed'
        )
        return api_template

    def create_template(self, creating_data: Dict) -> Dict:
        """Create a new template, persist it in the db, start async creation.

        Args:
            creating_data (Dict): A dictionary with template creation fields.

        Returns:
            Dict: A serialized representation of the newly created template.
        """
        LOG.info('Service layer handle request on creating template')

        creating_command = CreateTemplateServiceCommandDTO.model_validate(
            creating_data
        )

        volume = self._get_volume_info(creating_command.base_volume_id)
        storage = self._get_storage_info(creating_command.storage_id)

        path = (
            storage.mount_point
            / f'template-{creating_command.name}.{volume.format}'
        )
        tmp_format = volume.format

        new_template_model = CreateTemplateModelDTO(
            name=creating_command.name,
            description=creating_command.description,
            path=path,
            tmp_format=tmp_format,
            storage_id=creating_command.storage_id,
            is_backing=creating_command.is_backing,
        )
        orm_template = CreateSerializer.to_orm(new_template_model)
        with self.uow as uow:
            uow.templates.add(orm_template)
            uow.commit()
        self._update_and_log_event(
            orm_template, TemplateStatus.NEW, 'TemplateCreationPrepared'
        )

        async_creating_command = AsyncCreateTemplateServiceCommandDTO(
            id=orm_template.id,
            source_disk_path=volume.path / f'volume-{volume.id}',
        )
        self.service_layer_rpc.cast(
            self._create_template.__name__,
            data_for_method=async_creating_command.model_dump(mode='json'),
        )

        LOG.info(
            'Service layer request on creating template'
            'was successfully processed'
        )
        api_template: Dict[str, Any] = ApiSerializer.to_dict(orm_template)
        return api_template

    def edit_template(self, updating_data: Dict) -> Dict:
        """Initiate the editing process for an existing template.

        Args:
            updating_data (Dict): A dictionary with updated template fields.

        Returns:
            Dict: A serialized representation of the template being edited.
        """
        edit_command = EditTemplateServiceCommandDTO.model_validate(
            updating_data
        )
        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(edit_command.id)
        self._ensure_template_not_in_use(orm_template)

        self._update_and_log_event(
            orm_template, TemplateStatus.EDITING, 'TemplateEditingStarted'
        )

        self.service_layer_rpc.cast(
            self._edit_template.__name__,
            data_for_method=edit_command.model_dump(mode='json'),
        )
        return ApiSerializer.to_dict(orm_template)

    def delete_template(self, deleting_data: Dict) -> Dict:
        """Initiate the deletion process for a template.

        Args:
            deleting_data (Dict): A dictionary containing the template ID.

        Returns:
            Dict: A serialized representation of the template marked for
                deletion.
        """
        delete_command = DeleteTemplateServiceCommandDTO.model_validate(
            deleting_data
        )
        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(delete_command.id)
        self._ensure_template_not_in_use(orm_template)

        self._update_and_log_event(
            orm_template, TemplateStatus.DELETING, 'TemplateDeletingStarted'
        )

        self.service_layer_rpc.cast(
            self._delete_template.__name__,
            data_for_method=delete_command.model_dump(mode='json'),
        )

        return ApiSerializer.to_dict(orm_template)

    def _create_template(self, prepared_create_command_data: Dict) -> None:
        """Perform the async creation of a template file via the domain layer.

        This method is invoked via cast-RPC after initial template DB
        registration.

        Args:
            prepared_create_command_data (Dict): Data containing template ID and
                source volume path.

        Raises:
            RpcException: If domain RPC call fails.
        """
        async_creating_command = (
            AsyncCreateTemplateServiceCommandDTO.model_validate(
                prepared_create_command_data
            )
        )
        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(async_creating_command.id)

        self._update_and_log_event(
            orm_template, TemplateStatus.CREATING, 'TemplateCreationStarted'
        )

        try:
            domain_template = DomainSerializer.to_dto(orm_template)
            creation_domain_command_dto = CreateTemplateDomainCommandDTO(
                source_disk_path=async_creating_command.source_disk_path
            )
            domain_result: Dict = self.domain_rpc.call(
                BaseTemplate.create.__name__,
                data_for_manager=domain_template.model_dump(mode='json'),
                data_for_method=creation_domain_command_dto.model_dump(
                    mode='json'
                ),
            )
        except RpcException as err:
            self._update_and_log_event(
                orm_template,
                TemplateStatus.ERROR,
                'TemplateCreationFailed',
                str(err),
            )
            LOG.error('Error while creating template', exc_info=True)
            return
        orm_template = DomainSerializer.update_orm_from_dict(
            orm_template,
            domain_result,
        )
        self._update_and_log_event(
            orm_template, TemplateStatus.AVAILABLE, 'TemplateCreated'
        )

    def _edit_template(self, edit_command_data: Dict) -> None:
        """Perform the async renaming/editing of a template via the domain layer

        Args:
            edit_command_data (Dict): Serialized DTO with updated name and
                description.

        Raises:
            RpcException: If domain RPC call fails.
        """
        edit_command = EditTemplateServiceCommandDTO.model_validate(
            edit_command_data
        )

        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(edit_command.id)

        try:
            data_for_manager = DomainSerializer.to_dto(orm_template)
            data_for_manager.related_volumes = self._get_related_volumes(
                orm_template.id,
                orm_template.storage_id,
            )
            data_for_method = EditTemplateDomainCommandDTO.model_validate(
                edit_command_data
            )
            domain_result = self.domain_rpc.call(
                BaseTemplate.edit.__name__,
                data_for_manager=data_for_manager.model_dump(mode='json'),
                data_for_method=data_for_method.model_dump(mode='json'),
            )
        except RpcException as err:
            self._update_and_log_event(
                orm_template,
                TemplateStatus.ERROR,
                'TemplateEditingFailed',
                str(err),
            )
            LOG.error('Error while editing template', exc_info=True)
            return
        orm_template = DomainSerializer.update_orm_from_dict(
            orm_template,
            domain_result,
        )
        self._update_and_log_event(
            orm_template, TemplateStatus.AVAILABLE, 'TemplateEdited'
        )

    def _delete_template(self, delete_command_data: Dict) -> None:
        """Delete a template file from the filesystem and remove the DB record.

        Args:
            delete_command_data (Dict): Dictionary containing the template ID.

        Raises:
            RpcException: If domain RPC call fails.
        """
        delete_command = DeleteTemplateServiceCommandDTO.model_validate(
            delete_command_data
        )
        with self.uow as uow:
            orm_template = uow.templates.get_or_fail(delete_command.id)
        try:
            data_for_manager = DomainSerializer.to_dto(orm_template)
            data_for_manager.related_volumes = self._get_related_volumes(
                orm_template.id,
                orm_template.storage_id,
            )
            self.domain_rpc.call(
                BaseTemplate.delete.__name__,
                data_for_manager=data_for_manager.model_dump(mode='json'),
            )
        except RpcException as err:
            self._update_and_log_event(
                orm_template,
                TemplateStatus.ERROR,
                'TemplateDeletingFailed',
                str(err),
            )
            LOG.error('Error while deleting template', exc_info=True)
            return

        with self.uow as uow:
            uow.templates.delete(orm_template)
            uow.commit()

    def _ensure_template_not_in_use(self, orm_template: Template) -> None:
        """Check if the template is safe to edit or delete.

        Args:
            orm_template (Template): ORM instance of the template.

        Raises:
            Exception: If template is still referenced by volumes.
        """
        data_for_manager = DomainSerializer.to_dto(orm_template)
        data_for_manager.related_volumes = self._get_related_volumes(
            orm_template.id,
            orm_template.storage_id,
        )
        self.domain_rpc.call(
            BaseTemplate.ensure_not_in_use.__name__,
            data_for_manager=data_for_manager.model_dump(mode='json'),
        )

    def _update_and_log_event(
        self,
        orm_template: Template,
        status: TemplateStatus,
        event_type: str,
        message: str = '',
    ) -> None:
        """Update template status and persist an audit event.

        Args:
            orm_template (Template): Template ORM object to update.
            status (TemplateStatus): New status to apply.
            event_type (str): Type of event to log.
            message (str, optional): Additional context or error message.
        """
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

    def _get_volume_info(self, volume_id: UUID) -> VolumeModelDTO:
        """Fetch detailed information about a volume via RPC.

        Args:
            volume_id (UUID): ID of the base volume.

        Returns:
            VolumeModelDTO: Volume model containing metadata.

        Raises:
            VolumeRetrievalException: If RPC fails or volume is not found.
        """
        volume_query_payload = GetVolumeCommandDTO(
            volume_id=volume_id
        ).model_dump(mode='json')
        try:
            volume_data = self.volume_service_client.get_volume(
                volume_query_payload
            )
            return VolumeModelDTO.model_validate(volume_data)

        except RpcException as rpc_volume_err:
            LOG.error(
                f'Error while getting base volume with id: {volume_id}',
                exc_info=True,
            )
            message = f'Failed to get volume with id {volume_id}'
            raise VolumeRetrievalException(message) from rpc_volume_err

    def _get_volumes(
        self, storage_id: Optional[UUID] = None
    ) -> List[VolumeModelDTO]:
        """Retrieve all volumes from the volume service.

        Optionally filtered by storage.

        Args:
            storage_id (Optional[UUID]): Filter volumes by this storage.

        Returns:
            List[VolumeModelDTO]: List of validated volume models.

        Raises:
            VolumeRetrievalException: If RPC call fails.
        """
        LOG.info('Getting all volumes...')
        try:
            volumes_info = self.volume_service_client.get_all_volumes(
                {'storage_id': str(storage_id)}
            )
        except RpcException as rpc_volume_err:
            LOG.error('Error while getting volumes', exc_info=True)
            message = 'Failed to get volumes'
            raise VolumeRetrievalException(message) from rpc_volume_err
        return [
            VolumeModelDTO.model_validate(vol_info) for vol_info in volumes_info
        ]

    def _get_related_volumes(
        self, template_id: UUID, storage_id: UUID
    ) -> List[str]:
        """Get names of volumes that were created from the given template.

        Args:
            template_id (UUID): Template UUID to search references for.
            storage_id (UUID): Storage ID to limit volume search.

        Returns:
            List[str]: Names of volumes referencing the template.
        """
        LOG.info(f'Filtering volumes with reff on template {template_id}...')
        related_volumes = list(
            filter(
                lambda x: x.template_id == template_id,
                self._get_volumes(storage_id),
            )
        )
        return [volume.name for volume in related_volumes]

    def _get_storage_info(self, storage_id: UUID) -> StorageModelDTO:
        """Fetch metadata about a specific storage via RPC.

        Args:
            storage_id (UUID): ID of the storage to retrieve.

        Returns:
            StorageModelDTO: Storage information object.

        Raises:
            StorageRetrievalException: If storage is not found or RPC fails.
        """
        storage_query_payload = GetStorageCommandDTO(
            storage_id=storage_id
        ).model_dump(mode='json')
        try:
            storage_data = self.storage_service_client.get_storage(
                storage_query_payload
            )
            return StorageModelDTO.model_validate(storage_data)
        except RpcException as rpc_storage_err:
            LOG.error(
                f'Error while getting base storage with id: ' f'{storage_id}',
                exc_info=True,
            )
            message = f'Failed to get storage with id {storage_id}'
            raise StorageRetrievalException(message) from rpc_storage_err
