"""API module for volume management.

This module defines API endpoints for managing volumes, including operations
like creating, retrieving, updating, and deleting volumes. The API routes
handle requests and pass them to the underlying service layer for processing.

Endpoints:
    - GET /volumes/: Retrieve a paginated list of all volumes or filter by
        storage.
    - GET /volumes/{volume_id}/: Retrieve detailed information for a specific
        volume.
    - POST /volumes/create/: Create a new volume.
    - DELETE /volumes/{volume_id}/: Delete an existing volume.
    - POST /volumes/{volume_id}/extend/: Extend an existing volume to a new
        size.
    - PUT /volumes/{volume_id}/edit/: Edit an existing volume's metadata.
    - POST /volumes/{volume_id}/attach/: Attach a volume to a virtual machine.
    - DELETE /volumes/{volume_id}/detach/: Detach a volume from a virtual
        machine.
"""

from typing import Dict, Optional, cast

from fastapi import Path, Query, Depends, APIRouter, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import get_current_user
from openvair.libs.validation.validators import regex_matcher, validate_objects
from openvair.modules.volume.entrypoints import schemas
from openvair.modules.volume.entrypoints.crud import VolumeCrud

LOG = get_logger(__name__)
UUID_REGEX = regex_matcher('uuid4')

router = APIRouter(
    prefix='/volumes',
    tags=['volume'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=Page[schemas.Volume],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_volumes(
    storage_id: Optional[str] = Query(
        default=None, description='Storage id (UUID4)', regex=UUID_REGEX
    ),
    *,
    free_volumes: bool = Query(
        default=False,
        description='Flag on getting volumes without attachments.',
    ),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> Page:
    """Retrieve all volumes from the database.

    Args:
        storage_id (Optional[str]): The ID of the storage to filter volumes by.
        free_volumes (Optional[bool]): If True, return only volumes without
            attachments.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: A paginated list of volumes.
    """
    LOG.info('Api handle response on getting volumes.')
    result = await run_in_threadpool(
        crud.get_all_volumes, storage_id, free_volumes=free_volumes
    )
    volumes = validate_objects(result, schemas.Volume)

    LOG.info('Api request was successfully processed.')
    return cast(Page, paginate(volumes))


@router.get(
    '/{volume_id}/',
    response_model=schemas.Volume,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_volume(
    volume_id: str = Path(
        ..., description='Volume id (UUID4)', regex=UUID_REGEX
    ),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Retrieve a specific volume by its ID.

    Args:
        volume_id (str): The ID of the volume to retrieve.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: The serialized volume object.
    """
    LOG.info('Api handle response on getting volume.')
    volume = await run_in_threadpool(crud.get_volume, volume_id)
    LOG.info('Api request was successfully processed.')
    return JSONResponse(volume)


@router.post(
    '/create/',
    response_model=schemas.Volume,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_volume(
    data: schemas.CreateVolume,
    user_info: Dict = Depends(get_current_user),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Create a new volume.

    Args:
        data (schemas.CreateVolume): The data required to create the volume.
        user_info (Dict): Information about the authenticated user.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: The created volume object.
    """
    LOG.info('Api handle response on create volume with data: %s' % data)
    volume = await run_in_threadpool(crud.create_volume, data.dict(), user_info)
    LOG.info('Api request was successfully processed.')
    return JSONResponse(volume)


@router.delete(
    '/{volume_id}/',
    response_model=schemas.Volume,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_current_user)],
)
async def delete_volume(
    volume_id: str = Path(
        ..., description='Volume id (UUID4)', regex=UUID_REGEX
    ),
    user_info: Dict = Depends(get_current_user),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Delete an existing volume.

    Args:
        volume_id (str): The ID of the volume to delete.
        user_info (Dict): Information about the authenticated user.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: The deleted volume object.
    """
    LOG.info('Api handle response on delete volume: %s' % volume_id)
    result = await run_in_threadpool(crud.delete_volume, volume_id, user_info)
    LOG.info('Api request was successfully processed.')
    return JSONResponse(result)


@router.post(
    '/{volume_id}/extend/',
    response_model=schemas.Volume,
    status_code=status.HTTP_201_CREATED,
)
async def extend_volume(
    data: schemas.ExtendVolume,
    volume_id: str = Path(
        ..., description='Volume id (UUID4)', regex=UUID_REGEX
    ),
    user_info: Dict = Depends(get_current_user),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Extend an existing volume to a new size.

    Args:
        volume_id (str): The ID of the volume to extend.
        data (schemas.ExtendVolume): The new size of the volume.
        user_info (Dict): Information about the authenticated user.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: The extended volume object.
    """
    LOG.info('Api handle response on extend volume: %s' % volume_id)
    volume = await run_in_threadpool(
        crud.extend_volume, volume_id, data.dict(), user_info
    )
    LOG.info('Api request was successfully processed.')
    return JSONResponse(volume)


@router.put(
    '/{volume_id}/edit/',
    response_model=schemas.Volume,
    status_code=status.HTTP_201_CREATED,
)
async def edit_volume(
    data: schemas.EditVolume,
    volume_id: str = Path(
        ..., description='Volume id (UUID4)', regex=UUID_REGEX
    ),
    user_info: Dict = Depends(get_current_user),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Edit an existing volume's metadata.

    Args:
        volume_id (str): The ID of the volume to edit.
        data (schemas.EditVolume): The new metadata for the volume.
        user_info (Dict): Information about the authenticated user.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: The updated volume object.
    """
    LOG.info(
        'Api handle response on edit volume: %s with data:' % volume_id,
        data.dict(),
    )
    volume = await run_in_threadpool(
        crud.edit_volume, volume_id, data.dict(), user_info
    )
    LOG.info('Api request was successfully processed.')
    return JSONResponse(volume)


@router.post(
    '/{volume_id}/attach/',
    response_model=schemas.AttachVolumeInfo,
    status_code=status.HTTP_201_CREATED,
)
async def attach_volume(
    data: schemas.AttachVolume,
    volume_id: str = Path(
        ..., description='Volume id (UUID4)', regex=UUID_REGEX
    ),
    user_info: Dict = Depends(get_current_user),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Attach a volume to a virtual machine.

    Args:
        volume_id (str): The ID of the volume to be attached.
        data (schemas.AttachVolume): Information about the attachment.
        user_info (Dict): Information about the authenticated user.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: Information about the attached volume.
    """
    LOG.info(
        'Api handle response on attach volume: %s with data:' % volume_id,
        data.dict(),
    )
    attached_volume = await run_in_threadpool(
        crud.attach_volume, volume_id, data.dict(), user_info
    )
    LOG.info('Api request was successfully processed.')
    return JSONResponse(attached_volume)


@router.delete(
    '/{volume_id}/detach/',
    response_model=schemas.Volume,
    status_code=status.HTTP_201_CREATED,
)
async def detach_volume(
    detach_info: schemas.DetachVolume,
    volume_id: str = Path(
        ..., description='Volume id (UUID4)', regex=UUID_REGEX
    ),
    user_info: Dict = Depends(get_current_user),
    crud: VolumeCrud = Depends(VolumeCrud),
) -> JSONResponse:
    """Detach a volume from a virtual machine.

    Args:
        volume_id (str): The ID of the volume to be detached.
        detach_info (schemas.DetachVolume): Information about the detachment.
        user_info (Dict): Information about the authenticated user.
        crud (VolumeCrud): Dependency that handles the CRUD operations.

    Returns:
        JSONResponse: The detached volume object.
    """
    LOG.info(
        'Api handle response on detach ' 'volume: %s with data:' % volume_id
    )
    detached_volume = await run_in_threadpool(
        crud.detach_volume, volume_id, detach_info.dict(), user_info
    )
    LOG.info('Api request was successfully processed.')
    return JSONResponse(detached_volume)
