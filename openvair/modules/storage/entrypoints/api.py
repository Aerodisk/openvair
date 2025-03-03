"""API entrypoints for storage-related operations.

This module defines the REST API endpoints for managing storage and local disk
partitions. It includes endpoints for retrieving storage information, creating
and deleting storages, and managing local disk partitions.

Entrypoints:
    GET /storages/ - Retrieve a list of storages.
    GET /storages/local-disks/ - Retrieve a list of free local disks.
    POST /storages/local-disks/create_partition/ - Create a local disk
        partition.
    GET /storages/local-disks/partition_info/ - Get information about local
        disk partitions.
    DELETE /storages/local-disks/delete_partition/ - Delete a local disk
        partition.
    GET /storages/{storage_id}/ - Retrieve a storage by its ID.
    POST /storages/create/ - Create a new storage.
    DELETE /storages/{storage_id}/delete/ - Delete a storage by its ID.
"""

from uuid import UUID
from typing import Dict, Optional, cast

from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.storage.entrypoints import schemas
from openvair.modules.storage.entrypoints.crud import StorageCrud

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/storages',
    tags=['storage'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=Page[schemas.Storage],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_storages(
    crud: StorageCrud = Depends(StorageCrud),
) -> Page[schemas.Storage]:
    """It gets a list of storages from the database

    Args:
        crud: Depends (StorageCrud) - this is a dependency injection.

    Returns:
        A list of storages.
    """
    LOG.info('Api start getting list of storages')
    storages = await run_in_threadpool(crud.get_all_storages)
    LOG.info('Api request was successfully processed.')
    return cast(Page, paginate(storages))


@router.get(
    '/local-disks/',
    response_model=schemas.ListOfLocalDisks,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_local_disks(
    free_local_disks: Optional[bool] = None,
    crud: StorageCrud = Depends(StorageCrud),
) -> schemas.ListOfLocalDisks:
    """It gets a list of free local disks

    Args:
        free_local_disks: flag on get free local disks
        crud: This is the dependency that we created earlier.

    Returns:
        A list of free local disks.
    """
    LOG.info('Api start getting list of local disks')
    data = {'free_local_disks': free_local_disks}
    local_disks = await run_in_threadpool(crud.get_local_disks, data)
    LOG.info('Api request was successfully processed.')
    return local_disks


@router.post(
    '/local-disks/create_partition/',
    response_model=schemas.LocalDisk,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def create_local_partition(
    data: schemas.CreateLocalPartition,
    user_data: Dict = Depends(get_current_user),
    crud: StorageCrud = Depends(StorageCrud),
) -> schemas.LocalDisk:
    """Create a local disk partition.

    This endpoint creates a new partition on a local disk based on the provided
    data.

    Args:
        data (schemas.CreateLocalPartition): Data for creating the partition.
        crud (StorageCrud): Dependency for CRUD operations.
        user_data (Dict): User data

    Returns:
        schemas.LocalDisk: Information about the newly created partition.
    """
    LOG.info('Api start create partition on local disk')
    result = await run_in_threadpool(
        crud.create_local_partition, data.model_dump(mode='json'), user_data
    )
    LOG.info('Api request was successfully processed.')
    return schemas.LocalDisk(**result)


@router.get(
    '/local-disks/partition_info/',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_local_disk_partitions_info(
    disk_path: str, crud: StorageCrud = Depends(StorageCrud)
) -> JSONResponse:
    """Get information about local disk partitions.

    This endpoint retrieves information about partitions on a specified local
    disk.

    Args:
        disk_path (str): Path to the local disk.
        unit (Optional[str]): unit of values about partitions
        crud (StorageCrud): Dependency for CRUD operations.

    Returns:
        Dict: Information about local disk partitions.
    """
    LOG.info('Api start getting list of partitions')
    return JSONResponse(
        (
            await run_in_threadpool(
                crud.get_local_disk_partitions_info,
                {
                    'disk_path': disk_path,
                },
            )
        )
    )


@router.delete(
    '/local-disks/delete_partition/',
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_local_partition(
    data: schemas.DeleteLocalPartition,
    user_data: Dict = Depends(get_current_user),
    crud: StorageCrud = Depends(StorageCrud),
) -> JSONResponse:
    """Delete a local disk partition.

    This endpoint deletes the specified local disk partition.

    Args:
        data (schemas.DeleteLocalPartition): Data for deleting the partition.
        crud (StorageCrud): Dependency for CRUD operations.
        user_data (Dict): User data

    Returns:
        Dict: A message indicating the success of the operation.
    """
    LOG.info('Api start delete partition on local disk')
    result = await run_in_threadpool(
        crud.delete_local_partition, data.model_dump(mode='json'), user_data
    )
    LOG.info('Api request was successfully processed.')
    return JSONResponse(result)


@router.get(
    '/{storage_id}/',
    response_model=schemas.Storage,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_storage(
    storage_id: UUID,
    crud: StorageCrud = Depends(StorageCrud),
) -> schemas.Storage:
    """It gets a storage by id

    Args:
        storage_id (str): str = Query(None, description="Volume id")
        crud: Depends(StorageCrud) - this is a dependency injection.

    Returns:
        The storage object.
    """
    LOG.info('Api handle response on getting storage.')
    storage = await run_in_threadpool(crud.get_storage, storage_id)
    LOG.info('Api request was successfully processed.')
    return schemas.Storage(**storage)


@router.post(
    '/create/',
    response_model=schemas.Storage,
    status_code=status.HTTP_201_CREATED,
)
async def create_storage(
    data: schemas.CreateStorage,
    user_data: Dict = Depends(get_current_user),
    crud: StorageCrud = Depends(StorageCrud),
) -> schemas.Storage:
    """It creates a storage

    Args:
        data (schemas.CreateStorage): schemas.CreateStorage - this is the data
        that will be passed to the function.
        user_data: The dependency that check user was authorised
        crud: StorageCrud - this is the dependency that we will inject into the
        function.

    Returns:
        The storage object is being returned.
    """
    LOG.info(
        'Api start creating storage with data: %s.'
        % data.model_dump(mode='json')
    )
    storage = await run_in_threadpool(
        crud.create_storage, data.model_dump(mode='json'), user_data
    )
    LOG.info('Api request was successfully processed.')
    return schemas.Storage(**storage)


@router.delete(
    '/{storage_id}/delete/',
    response_model=schemas.Storage,
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_storage(
    storage_id: UUID,
    user_data: Dict = Depends(get_current_user),
    crud: StorageCrud = Depends(StorageCrud),
) -> schemas.Storage:
    """It deletes a storage

    Args:
        storage_id (str): str = Query(None, description="Storage id")
        user_data: The dependency that check user was authorised
        crud: Depends(StorageCrud)

    Returns:
        The storage object.
    """
    LOG.info('Api start deleting storage: %s.' % storage_id)
    storage = await run_in_threadpool(
        crud.delete_storage, storage_id, user_data
    )
    LOG.info('Api request was successfully processed.')
    return schemas.Storage(**storage)
