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
from typing import List

from pydantic import BaseModel

from openvair.libs.log import get_logger
from openvair.modules.template.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.template.entrypoints.schemas import Volume, BaseTemplate
from openvair.modules.template.service_layer.services import (
    TemplateServiceLayerManager,
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

    def get_all_templates(self) -> List[BaseTemplate]:
        """Retrieve a list of all templates via RPC.

        Returns:
            List[Template]: A list of all available templates.
        """
        LOG.info('Starting retrieval of all templates.')
        result = self.service_layer_rpc.call(
            TemplateServiceLayerManager.get_all_templates.__name__,
            data_for_method={},
        )
        templates = [BaseTemplate.model_validate(item) for item in result]
        LOG.info(
            f'Finished retrieval of all templates. Retrieved {len(templates)} '
            'templates.'
        )
        return templates

    def get_template(self, template_id: UUID) -> BaseTemplate:
        """Retrieve a specific template by its ID via RPC.

        Args:
            template_id (UUID): The ID of the template to retrieve.

        Returns:
            Template: The retrieved template object.
        """
        LOG.info(f'Starting retrieval of template with ID: {template_id}.')
        result = self.service_layer_rpc.call(
            TemplateServiceLayerManager.get_template.__name__,
            data_for_method={'template_id': str(template_id)},
        )
        template = BaseTemplate.model_validate(result)
        LOG.info(f'Finished retrieval of template with ID: {template_id}.')
        return template

    def create_template(self, data: BaseModel) -> BaseTemplate:
        """Create a new template using provided data via RPC.

        Args:
            data (BaseModel): The template creation data.

        Returns:
            Template: The created template object.
        """
        LOG.info('Starting creation of a new template.')
        result = self.service_layer_rpc.call(
            TemplateServiceLayerManager.create_template.__name__,
            data_for_method=data.model_dump(mode='json'),
        )
        template = BaseTemplate.model_validate(result)
        LOG.info(f"Finished creation of template '{template.name}'.")
        return template

    def update_template(
        self,
        template_id: UUID,
        data: BaseModel,
    ) -> BaseTemplate:
        """Update an existing template using partial data via RPC.

        Args:
            template_id (UUID): The ID of the template to update.
            data (BaseModel): The updated fields for the template.

        Returns:
            Template: The updated template object.
        """
        LOG.info(f'Starting update of template with ID: {template_id}.')
        params = {'template_id': str(template_id)}
        params.update(data.model_dump(exclude_unset=True, mode='json'))
        result = self.service_layer_rpc.call(
            TemplateServiceLayerManager.update_template.__name__,
            data_for_method=params,
        )
        template = BaseTemplate.model_validate(result)
        LOG.info(f'Finished update of template with ID: {template_id}.')
        return template

    def delete_template(self, template_id: UUID) -> BaseTemplate:
        """Delete a template by its ID via RPC.

        Args:
            template_id (UUID): The ID of the template to delete.

        Returns:
            Template: The deleted template object.
        """
        LOG.info(f'Starting deletion of template with ID: {template_id}.')
        result = self.service_layer_rpc.call(
            TemplateServiceLayerManager.delete_template.__name__,
            data_for_method={'template_id': str(template_id)},
        )
        template = BaseTemplate.model_validate(result)
        LOG.info(f'Finished deletion of template with ID: {template_id}.')
        return template

    def create_volume_from_template(
        self,
        template_id: UUID,
        data: BaseModel,
    ) -> Volume:
        """Create a volume based on the specified template via RPC.

        Args:
            template_id (UUID): The ID of the template to use.
            data (BaseModel): Parameters for the volume creation.

        Returns:
            Volume: The created volume object.
        """
        LOG.info(
            f'Starting creation of volume from template with ID: {template_id}.'
        )
        params = {'template_id': str(template_id)}
        params.update(data.model_dump(mode='json'))
        result = self.service_layer_rpc.call(
            TemplateServiceLayerManager.create_volume_from_template.__name__,
            data_for_method=params,
        )
        volume = Volume.model_validate(result)
        LOG.info(
            f"Finished creation of volume '{volume.name}' from template "
            f'with ID: {template_id}.'
        )
        return volume
