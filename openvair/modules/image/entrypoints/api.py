"""API module for managing images.

This module defines a FastAPI router with endpoints for managing images,
including retrieving image metadata, uploading, deleting, and attaching
or detaching images to/from virtual machines (VMs). It provides a RESTful
interface for image operations.

Endpoints:
    - GET `/images/`: Retrieve a list of images with optional filtering by
        storage.
    - GET `/images/{image_id}/`: Retrieve metadata of a specific image by ID.
    - POST `/images/upload/`: Upload a new image to a storage.
    - DELETE `/images/{image_id}/`: Delete an image by ID.
    - POST `/images/{image_id}/attach/`: Attach an image to a virtual machine.
    - DELETE `/images/{image_id}/detach/`: Detach an image from a virtual
        machine.
"""

from uuid import UUID
from typing import Dict, Optional, cast
from pathlib import Path

import aiofiles
from fastapi import (
    File,
    Query,
    Depends,
    APIRouter,
    UploadFile,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from starlette.concurrency import run_in_threadpool

from openvair.config import TMP_DIR
from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.image.config import CHUNK_SIZE
from openvair.modules.image.entrypoints import schemas, exceptions
from openvair.modules.image.entrypoints.crud import ImageCrud

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/images',
    tags=['image'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=Page[schemas.Image],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_images(
    storage_id: Optional[UUID] = Query(
        default=None,
        description='Storage id (UUID4)',
    ),
    crud: ImageCrud = Depends(ImageCrud),
) -> Page[schemas.Image]:
    """Retrieve a paginated list of images.

    This endpoint allows retrieving all images stored in the database, with
    an optional filter by a specific storage ID. It uses the `ImageCrud`
    service to interact with the storage backend.

    Args:
        storage_id (Optional[str]): Storage ID to filter images by.
        crud (ImageCrud): Dependency injection for CRUD operations.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        Page[schemas.Image]: A paginated response containing metadata of
        images matching the filter criteria, if provided.
    """
    LOG.info('Api start getting list of images')
    images = await run_in_threadpool(crud.get_all_images, storage_id)
    LOG.info('Api request was successfully processed.')
    return cast('Page', paginate(images))


@router.get(
    '/{image_id}/',
    response_model=schemas.Image,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_image(
    image_id: UUID,
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.Image:
    """Retrieve metadata of a specific image by its ID.

    This endpoint fetches metadata of an image specified by its ID using
    the `ImageCrud` service.

    Args:
        image_id (str): ID of the image to retrieve.
        crud (ImageCrud): Dependency injection for CRUD operations.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        schemas.Image: Metadata of the specified image.
    """
    LOG.info('Api handle response on get image.')
    image = await run_in_threadpool(crud.get_image, image_id)
    LOG.info('Api request was successfully processed.')
    return schemas.Image(**image)


@router.post(
    '/upload/',
    response_model=schemas.Image,
    status_code=status.HTTP_200_OK,
)
async def upload_image(  # noqa: PLR0913 не возможно передать аргументы как Pydantic схему или Dict,
    # потому что запрос в формате multipart/form-data из-за использования
    # File(...) для загрузки файла. FastAPI не умеет автоматически парсить
    # Pydantic-модель или Dict из тела запроса, если запрос multipart/form-data.
    storage_id: UUID,
    description: str = Query(
        default='',
        description='Image description',
    ),
    name: str = Query(
        max_size=40,
        description='Image name',
    ),
    image: UploadFile = File(..., description='Upload image.'),
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.Image:
    """Upload a new image to the storage.

    This endpoint reads the uploaded image file, saves it temporarily, and
    uploads it to the specified storage using the `ImageCrud` service.

    Args:
        description (str): Description of the image.
        storage_id (str): ID of the storage where the image will be saved.
        name (str): Name of the image file.
        image (UploadFile): The uploaded image file.
        user_info (Dict): Authorized user information.
        crud (ImageCrud): Dependency injection for CRUD operations.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        schemas.Image: Metadata of the uploaded image.

    Raises:
        HTTPException: If the file name exceeds the allowed length or if
        the file extension is unsupported.
    """
    LOG.info(f'Api start uploading image: {name}')
    tmp_path = Path(TMP_DIR, name)
    try:
        async with aiofiles.open(tmp_path, 'wb') as f:
            while chunk := await image.read(CHUNK_SIZE):
                await f.write(chunk)
        await image.close()

        upload_info = await run_in_threadpool(
            crud.upload_image,
            name,
            storage_id,
            description,
            user_info,
        )
        LOG.info('Api request was successfully processed.')
    except exceptions.NotSupportedExtensionError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        )
    else:
        return schemas.Image(**upload_info)


@router.delete(
    '/{image_id}/',
    status_code=status.HTTP_200_OK,
)
async def delete_image(
    image_id: UUID,
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> JSONResponse:
    """Delete an image by its ID.

    This endpoint deletes an image specified by its ID using the `ImageCrud`
    service.

    Args:
        image_id (str): ID of the image to delete.
        user_info (Dict): Authorized user information.
        crud (ImageCrud): Dependency injection for CRUD operations.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        JSONResponse: A response confirming successful deletion.
    """
    LOG.info('Api handle response on delete image: %s.' % image_id)
    result = await run_in_threadpool(crud.delete_image, image_id, user_info)
    message = f'Image {image_id} successfully deleted.'
    LOG.info(message)
    return JSONResponse(result)


@router.post(
    '/{image_id}/attach/',
    response_model=schemas.AttachImageInfo,
    status_code=status.HTTP_201_CREATED,
)
async def attach_image(
    data: schemas.AttachImage,
    image_id: UUID,
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.AttachImageInfo:
    """Attach an image to a virtual machine (VM).

    This endpoint attaches an image specified by its ID to a virtual machine
    (VM) using the `ImageCrud` service.

    Args:
        data (schemas.AttachImage): Data containing the VM ID to which
        the image will be attached.
        image_id (str): ID of the image to attach.
        user_info (Dict): Authorized user information.
        crud (ImageCrud): Dependency injection for CRUD operations.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        schemas.AttachImageInfo: Metadata of the attached image.
    """
    LOG.info('Api handle response on attach image: %s to vm:' % image_id)
    attached_image = await run_in_threadpool(
        crud.attach_image, image_id, data.model_dump(mode='json'), user_info
    )
    LOG.info('Api request was successfully processed.')
    return schemas.AttachImageInfo(**attached_image)


@router.delete(
    '/{image_id}/detach/',
    response_model=schemas.Image,
    status_code=status.HTTP_201_CREATED,
)
async def detach_image(
    detach_info: schemas.DetachImage,
    image_id: UUID,
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.Image:
    """Detach an image from a virtual machine (VM).

    This endpoint detaches an image specified by its ID from a virtual
    machine (VM) using the `ImageCrud` service.

    Args:
        detach_info (schemas.DetachImage): Data containing the VM ID from
        which the image will be detached.
        image_id (str): ID of the image to detach.
        user_info (Dict): Authorized user information.
        crud (ImageCrud): Dependency injection for CRUD operations.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        schemas.Image: Metadata of the detached image.
    """
    LOG.info(
        'Api handle response on detach '
        'image: %s from vm: %s' % (image_id, detach_info)
    )
    detached_image = await run_in_threadpool(
        crud.detach_image,
        image_id,
        detach_info.model_dump(mode='json'),
        user_info,
    )
    LOG.info('Api request was successfully processed.')
    return schemas.Image(**detached_image)
