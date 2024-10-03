# noqa: D100
from typing import Dict, Optional
from pathlib import Path as Path_lib

import aiofiles
from fastapi import File, Path, Query, Depends, APIRouter, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import regex_matcher, get_current_user
from openvair.modules.image.config import TMP_DIR, CHUNK_SIZE
from openvair.modules.image.entrypoints import schemas, exceptions
from openvair.modules.image.entrypoints.crud import ImageCrud

LOG = get_logger(__name__)
UUID_REGEX = regex_matcher('uuid4')

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
    storage_id: Optional[str] = Query(
        default='',
        description='Storage id (UUID4)',
        regex=UUID_REGEX,
    ),
    crud: ImageCrud = Depends(ImageCrud),
) -> Page[schemas.Image]:
    """It gets all the images from the database and returns them

    Args:
        storage_id: Storage id
        crud: Depends(ImageCrud) - this is a dependency injection. It means
        that the function will receive an instance of ImageCrud class.

    Returns:
        Page[schemas.Image]: A list of images.
    """
    LOG.info('Api start getting list of images')
    images = await run_in_threadpool(crud.get_all_images, storage_id)
    LOG.info('Api request was successfully processed.')
    return images


@router.get(
    '/{image_id}/',
    response_model=schemas.Image,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_image(
    image_id: str = Path(
        default='', description='Image id (UUID4)', regex=UUID_REGEX
    ),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.Image:
    """Returns the image with the specified id

    It takes an image id, uses the ImageCrud dependency to get the image, and
    returns the image

    Args:
        image_id (str): str = Query(None, description="Image id")
        crud: Depends(ImageCrud) - this is a dependency injection. It means
        that the ImageCrud class will be instantiated and passed to
        the function as a parameter.

    Returns:
        schemas.Image: The image is being returned.
    """
    LOG.info('Api handle response on get image.')
    image = await run_in_threadpool(crud.get_image, image_id)
    LOG.info('Api request was successfully processed.')
    return image


@router.post(
    '/upload/',
    response_model=schemas.Image,
    status_code=status.HTTP_200_OK,
)
async def upload_image(  # noqa: PLR0913 need create a schema for arguments
    description: str = Query(
        default='',
        description='Image description',
    ),
    storage_id: str = Query(
        default='', description='Storage id (UUID4)', regex=UUID_REGEX
    ),
    name: str = Query(
        default='',
        description='Image name',
    ),
    image: UploadFile = File(..., description='Upload image.'),
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.Image:
    """Uploads an image to the storage.

    It reads the image from the request, saves it to a temporary file,
    and then passes the file name to the `ImageCrud` class

    Args:
        storage_id (str): str - the id of the storage where the image will be
        uploaded
        name (str): str - the name of the image.
        description (str): str - the description of the image.
        image (UploadFile): UploadFile = File(...)
        user_info: The dependency that check user was authorised
        crud: Depends(ImageCrud) - this is a dependency injection.

    Returns:
        schemas.Image: The image object.
    """
    LOG.info(f'Api start uploading image: {name}')
    tmp_path = Path_lib(TMP_DIR, name)
    filename_length = 40
    try:
        if len(name) > filename_length:
            message = 'Length of filename must be lower then 40.'
            LOG.error(message)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=str(exceptions.FilenameLengthError(message)),
            )

        async with aiofiles.open(tmp_path, 'wb') as f:
            while chunk := await image.read(CHUNK_SIZE):
                await f.write(chunk)
        await image.close()

        image = await run_in_threadpool(
            crud.upload_image,
            name,
            storage_id,
            description,
            user_info,
        )
        LOG.info('Api request was successfully processed.')
    except exceptions.NotSupportedExtensionError as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(err)
        )
    else:
        return image


@router.delete(
    '/{image_id}/',
    status_code=status.HTTP_200_OK,
)
async def delete_image(
    image_id: str = Path(..., description='Image id (UUID4)', regex=UUID_REGEX),
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> JSONResponse:
    """It deletes an image from the database

    Args:
        image_id (str): str - the image id to delete
        user_info: The dependency that check user was authorised
        crud: This is the dependency that we created in the previous section.

    Returns:
        JSONResponse(status_code=status.HTTP_200_OK, content=message)
    """
    LOG.info('Api handle response on delete image: %s.' % image_id)
    result = await run_in_threadpool(crud.delete_image, image_id, user_info)
    message = f'Image {image_id} successfully deleted.'
    LOG.info(message)
    return result


@router.post(
    '/{image_id}/attach/',
    response_model=schemas.AttachImageInfo,
    status_code=status.HTTP_201_CREATED,
)
async def attach_image(
    data: schemas.AttachImage,
    image_id: str = Path(..., description='Image id (UUID4)', regex=UUID_REGEX),
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.AttachImageInfo:
    """Attach an image to a VM

    The first line of the function is a docstring. This is a string that
    describes what the function does. It's a good idea to include
    a docstring for every function you write

    Args:
        image_id (str): str - the id of the image to be attached
        data (str): str - the id of the VM to which the image will be attached
        user_info: The dependency that check user was authorised
        crud: This is the dependency that we created in the previous section.

    Returns:
        schemas.AttachImageInfo: The attached image.
    """
    LOG.info('Api handle response on attach image: %s to vm:' % image_id)
    attached_image = await run_in_threadpool(
        crud.attach_image, image_id, data.dict(), user_info
    )
    LOG.info('Api request was successfully processed.')
    return attached_image


@router.delete(
    '/{image_id}/detach/',
    response_model=schemas.Image,
    status_code=status.HTTP_201_CREATED,
)
async def detach_image(
    detach_info: schemas.DetachImage,
    image_id: str = Path(..., description='Image id (UUID4)', regex=UUID_REGEX),
    user_info: Dict = Depends(get_current_user),
    crud: ImageCrud = Depends(ImageCrud),
) -> schemas.Image:
    """It takes an image_id and a vm_id, and returns a detached_image

    Args:
        image_id (str): str - the id of the image to be detached
        detach_info (str): str - the id of the VM to which the image is attached
        user_info: The dependency that check user was authorised
        crud: Depends(ImageCrud) - this is a dependency injection.

    Returns:
        schemas.Image: The detached image.

    """
    LOG.info(
        'Api handle response on detach '
        'image: %s from vm: %s' % (image_id, detach_info)
    )
    detached_image = await run_in_threadpool(
        crud.detach_image, image_id, detach_info.dict(), user_info
    )
    LOG.info('Api request was successfully processed.')
    return detached_image
