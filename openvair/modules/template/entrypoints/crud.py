"""CRUD logic for template API entrypoints.

This module defines the TemplateCrud class, which acts as an adapter between
API endpoints and the service layer. All communication is performed via RPC.

Classes:
    - TemplateCrud: Provides methods for managing templates and creating
        volumes.

Dependencies:
    - MessagingClient: RPC client for service layer communication.
    - TemplateServiceLayerManager: Contains service layer method names.
"""

from uuid import UUID
from typing import Any, Dict, List

from openvair.libs.log import get_logger
from openvair.modules.template.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.template.service_layer.services import (
    TemplateServiceLayerManager,
)
from openvair.modules.template.entrypoints.schemas.requests import (
    RequestEditTemplate,
    RequestCreateTemplate,
)
from openvair.modules.template.entrypoints.schemas.responses import (
    TemplateResponse,
)
from openvair.modules.template.adapters.dto.internal.commands import (
    GetTemplateServiceCommandDTO,
    EditTemplateServiceCommandDTO,
    CreateTemplateServiceCommandDTO,
    DeleteTemplateServiceCommandDTO,
)

LOG = get_logger(__name__)


class TemplateCrud:
    """Provides RPC-based access to template service operations.

    This class encapsulates all logic required by the API layer to interact
    with the service layer for template and volume management.

    Attributes:
        service_layer_rpc (MessagingClient): RPC client for calling service
            methods.
    """

    def __init__(self) -> None:
        """Initialize the TemplateCrud instance.

        Sets up the RPC client for the template service layer.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_all_templates(self) -> List[TemplateResponse]:
        """Retrieve a list of all templates via RPC.

        Returns:
            List[Template]: A list of all available templates.
        """
        LOG.info('Call service layer on getting templates.')

        result: List[Dict[str, Any]] = self.service_layer_rpc.call(
            TemplateServiceLayerManager.get_all_templates.__name__,
            data_for_method={},
        )

        return [TemplateResponse.model_validate(item) for item in result]

    def get_template(self, template_id: UUID) -> TemplateResponse:
        """Retrieve a specific template by its ID via RPC.

        Args:
            template_id (UUID): The ID of the template to retrieve.

        Returns:
            Template: The retrieved template object.
        """
        LOG.info(f'Call service layer on getting template {template_id}.')

        getting_data = GetTemplateServiceCommandDTO(id=template_id)
        result: Dict[str, Any] = self.service_layer_rpc.call(
            TemplateServiceLayerManager.get_template.__name__,
            data_for_method=getting_data.model_dump(mode='json'),
        )

        return TemplateResponse.model_validate(result)

    def create_template(
        self, creation_data: RequestCreateTemplate
    ) -> TemplateResponse:
        """Create a new template using provided data via RPC.

        Args:
            creation_data (BaseModel): The template creation data.

        Returns:
            Template: The created template object.
        """
        LOG.info('Call service layer on creating new template.')

        input_dto = CreateTemplateServiceCommandDTO.model_validate(
            creation_data
        )
        result: Dict[str, Any] = self.service_layer_rpc.call(
            TemplateServiceLayerManager.create_template.__name__,
            data_for_method=input_dto.model_dump(mode='json'),
        )

        return TemplateResponse.model_validate(result)

    def edit_template(
        self,
        template_id: UUID,
        edit_data: RequestEditTemplate,
    ) -> TemplateResponse:
        """Update an existing template using partial data via RPC.

        Args:
            template_id (UUID): The ID of the template to update.
            edit_data (BaseModel): The updated fields for the template.

        Returns:
            Template: The updated template object.
        """
        LOG.info(f'Call service layer on editing template {template_id}.')

        edit_dto = EditTemplateServiceCommandDTO(
            id=template_id,
            name=edit_data.name,
            description=edit_data.description,
        )
        result: Dict[str, Any] = self.service_layer_rpc.call(
            TemplateServiceLayerManager.edit_template.__name__,
            data_for_method=edit_dto.model_dump(mode='json'),
        )
        return TemplateResponse.model_validate(result)


    def delete_template(self, template_id: UUID) -> TemplateResponse:
        """Delete a template by its ID via RPC.

        Args:
            template_id (UUID): The ID of the template to delete.

        Returns:
            Template: The deleted template object.
        """
        LOG.info(f'Call service layer on deleting template {template_id}.')

        deleting_data = DeleteTemplateServiceCommandDTO(id=template_id)
        result: Dict[str, Any] = self.service_layer_rpc.call(
            TemplateServiceLayerManager.delete_template.__name__,
            data_for_method=deleting_data.model_dump(mode='json'),
        )
        return TemplateResponse.model_validate(result)

