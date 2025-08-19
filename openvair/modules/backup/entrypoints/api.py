"""Module providing API endpoints for managing backups.

This module defines a FastAPI router with endpoints for managing backups,
including creating backups, restoring data, retrieving snapshots, deleting
snapshots, and initializing backup repositories.

Endpoints:
    - GET `/backup/`: Retrieve a list of backup snapshots.
    - POST `/backup/`: Create a new backup.
    - POST `/backup/restore`: Restore data from a specific snapshot.
    - POST `/backup/repository`: Initialize a backup repository.
    - DELETE `/backup/{snapshot_id}`: Delete a specific backup snapshot.
"""

from typing import List

from fastapi import Query, Depends, APIRouter
from fastapi.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.common.schemas import BaseResponse
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.backup.schemas import (
    ResticSnapshot,
    ResticBackupResult,
    ResticDeleteResult,
    ResticRestoreResult,
)
from openvair.modules.backup.entrypoints.crud import BackupCrud

LOG = get_logger(__name__)


router = APIRouter(
    prefix='/backup',
    tags=['backup'],
    responses={404: {'description': 'Not found!'}},
)


@router.post(
    '/',
    dependencies=[Depends(get_current_user)],
    response_model=BaseResponse[ResticBackupResult],
)
async def create_backup(
    crud: BackupCrud = Depends(BackupCrud),
) -> BaseResponse[ResticBackupResult]:
    """Create a new backup.

    This endpoint initiates a backup process using the `BackupCrud` service.

    Args:
        crud (BackupCrud): Dependency injection of the `BackupCrud` service.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        BaseResponse[ResticBackupResult]: A response containing the result
        of the backup operation.
    """
    LOG.info('API: Start creating a backup')
    backup_result = await run_in_threadpool(crud.create_backup)
    LOG.info('API: Backup successfully created.')
    return BaseResponse(status='success', data=backup_result)


@router.post(
    '/restore',
    dependencies=[Depends(get_current_user)],
    response_model=BaseResponse[ResticRestoreResult],
)
async def restore(
    snapshot_id: str = Query(
        'latest', description="Snapshot ID to restore (default: 'latest')"
    ),
    crud: BackupCrud = Depends(BackupCrud),
) -> BaseResponse[ResticRestoreResult]:
    """Restore data from a specific snapshot.

    This endpoint restores data from a specified snapshot using the
    `BackupCrud` service. The snapshot ID can be specified in the query
    parameters, with a default value of "latest".

    Args:
        snapshot_id (str): ID of the snapshot to restore. Defaults to "latest".
        crud (BackupCrud): Dependency injection of the `BackupCrud` service.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        BaseResponse[ResticRestoreResult]: A response containing the result
        of the restore operation.
    """
    LOG.info(f'API: Start restoring snapshot: {snapshot_id}')
    restore_data = await run_in_threadpool(crud.restore_backup, snapshot_id)
    LOG.info('API: Backup successfully created.')
    return BaseResponse(status='success', data=restore_data)


@router.get(
    '/',
    dependencies=[Depends(get_current_user)],
    response_model=BaseResponse[List[ResticSnapshot]],
)
async def get_backups(
    crud: BackupCrud = Depends(BackupCrud),
) -> BaseResponse[List[ResticSnapshot]]:
    """Retrieve a list of backup snapshots.

    This endpoint fetches all available backup snapshots using the
    `BackupCrud` service.

    Args:
        crud (BackupCrud): Dependency injection of the `BackupCrud` service.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        BaseResponse[List[ResticSnapshot]]: A response containing a list of
        snapshot metadata.
    """
    LOG.info('API: Start getting backup snapshots')
    snapshots = await run_in_threadpool(crud.get_snapshots)
    LOG.info('API: Snapshots received success')
    return BaseResponse(status='success', data=snapshots)


@router.post(
    '/repository',
    dependencies=[Depends(get_current_user)],
)
async def init_repository(
    crud: BackupCrud = Depends(BackupCrud),
) -> BaseResponse:
    """Initialize a backup repository.

    This endpoint initializes the backup repository using the `BackupCrud`
    service.

    Args:
        crud (BackupCrud): Dependency injection of the `BackupCrud` service.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        BaseResponse: A response indicating the success of the operation.
    """
    LOG.info('API: Start initializing repository')
    await run_in_threadpool(crud.initialize_backup_repository)
    LOG.info('API: Repository successfully inited')
    return BaseResponse(status='success')


@router.delete(
    '/{snapshot_id}',
    dependencies=[Depends(get_current_user)],
    response_model=BaseResponse[ResticDeleteResult],
)
async def delete_backup(
    snapshot_id: str,
    crud: BackupCrud = Depends(BackupCrud),
) -> BaseResponse[ResticDeleteResult]:
    """Delete a specific backup snapshot.

    This endpoint removes a backup snapshot by calling the `BackupCrud`.

    Args:
        snapshot_id (str): ID of the snapshot to delete.
        crud (BackupCrud): Dependency injection of the `BackupCrud`.

    Dependencies:
        - User authentication via `get_current_user`.

    Returns:
        BaseResponse[ResticDeleteResult]: A response containing the result
            of the deletion operation.
    """
    LOG.info(f'API: Start deleting snapshot: {snapshot_id}')
    result = await run_in_threadpool(crud.delete_snapshot, snapshot_id)
    LOG.info(f'API: Snapshot {snapshot_id} successfully deleted')
    LOG.info(result.message)
    return BaseResponse(status='success', data=result)
