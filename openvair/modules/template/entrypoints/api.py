"""API endpoints for managing templates.

This module defines the API routes for managing templates and creating
volumes from templates. All endpoints require user authentication.

Endpoints:
    - GET /templates/: Retrieve a list of templates.
    - GET /templates/{template_id}: Retrieve a specific template by ID.
    - POST /templates/: Create a new template.
    - PATCH /templates/{template_id}: Update an existing template.
    - DELETE /templates/{template_id}: Delete a template.
    - POST /templates/{template_id}/volumes: Create a volume from a template.

Dependencies:
    - get_current_user: Enforces authentication for all routes.
    - TemplateCrud: Service layer abstraction for performing business logic.
"""

from uuid import UUID
from typing import List

from fastapi import Depends, APIRouter, status
from fastapi_pagination import Page, Params, paginate
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.common.schemas import BaseResponse
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.template.entrypoints.crud import TemplateCrud
from openvair.modules.template.entrypoints.schemas.requests import (
    RequestEditTemplate,
    RequestCreateTemplate,
)
from openvair.modules.template.entrypoints.schemas.responses import (
    TemplateResponse,
)

LOG = get_logger(__name__)
router = APIRouter(
    prefix='/templates',
    tags=['templates'],
    dependencies=[
        Depends(get_current_user)
    ],  # Глобальная авторизация для всех эндпоинтов
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=BaseResponse[Page[TemplateResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_templates(
    crud: TemplateCrud = Depends(TemplateCrud),
    params: Params = Depends(),
) -> BaseResponse:
    """Retrieve a paginated list of templates.

    Args:
        crud (TemplateCrud): Dependency-injected service for handling template
            logic.
        params (Params): Dependency-injected for pagination params
    Returns:
        BaseResponse[Page[Template]]: Paginated response containing templates.
    """
    LOG.info('API: Getting list of templates')
    templates: List[TemplateResponse] = await run_in_threadpool(
        crud.get_all_templates
    )
    paginated_templates = paginate(templates, params)
    LOG.info('API: Finished getting list of templates')
    return BaseResponse(status='success', data=paginated_templates)


@router.get(
    '/{template_id}',
    response_model=BaseResponse[TemplateResponse],
    status_code=status.HTTP_200_OK,
)
async def get_template(
    template_id: UUID,
    crud: TemplateCrud = Depends(TemplateCrud),
) -> BaseResponse:
    """Retrieve a specific template by its ID.

    Args:
        template_id (UUID): The ID of the template to retrieve.
        crud (TemplateCrud): Dependency-injected service for handling template
            logic.

    Returns:
        BaseResponse[Template]: The retrieved template.
    """
    LOG.info(f'API: Getting template {template_id}')
    template = await run_in_threadpool(crud.get_template, template_id)
    LOG.info(f'API: Finished getting template {template_id}')
    return BaseResponse(status='success', data=template)


@router.post(
    '/',
    response_model=BaseResponse[TemplateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    data: RequestCreateTemplate,
    crud: TemplateCrud = Depends(TemplateCrud),
) -> BaseResponse:
    """Create a new template.

    Args:
        data (CreateTemplate): Template creation payload.
        crud (TemplateCrud): Dependency-injected service for handling template
            logic.

    Returns:
        BaseResponse[Template]: The created template.
    """
    LOG.info('API: Creating template')
    template = await run_in_threadpool(crud.create_template, data)
    LOG.info('API: Finished creating template')
    return BaseResponse(status='success', data=template)


@router.patch(
    '/{template_id}',
    response_model=BaseResponse[TemplateResponse],
    status_code=status.HTTP_200_OK,
)
async def update_template(
    template_id: UUID,
    data: RequestEditTemplate,
    crud: TemplateCrud = Depends(TemplateCrud),
) -> BaseResponse:
    """Update an existing template.

    Args:
        template_id (UUID): The ID of the template to update.
        data (EditTemplate): Fields to update in the template.
        crud (TemplateCrud): Dependency-injected service for handling template
            logic.

    Returns:
        BaseResponse[Template]: The updated template.
    """
    LOG.info(f'API: Updating template {template_id}')
    template = await run_in_threadpool(crud.edit_template, template_id, data)
    LOG.info(f'API: Finished updating template {template_id}')
    return BaseResponse(status='success', data=template)


@router.delete(
    '/{template_id}',
    response_model=BaseResponse[TemplateResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_template(
    template_id: UUID,
    crud: TemplateCrud = Depends(TemplateCrud),
) -> BaseResponse:
    """Delete a template by ID.

    Args:
        template_id (UUID): The ID of the template to delete.
        crud (TemplateCrud): Dependency-injected service for handling template
            logic.

    Returns:
        BaseResponse[Template]: The deleted template.
    """
    LOG.info(f'API: Deleting template {template_id}')
    template = await run_in_threadpool(crud.delete_template, template_id)
    LOG.info(f'API: Finished deleting template {template_id}')
    return BaseResponse(status='success', data=template)
