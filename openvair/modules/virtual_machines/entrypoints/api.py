"""Module for virtual machine API endpoints.

This module defines the FastAPI endpoints for managing virtual machines.
It includes operations such as retrieving, creating, deleting, starting,
shutting off, and editing virtual machines, as well as accessing VNC sessions.
The module uses dependency injection to manage the business logic through
the `VMCrud` class and ensures that users are authenticated before
performing actions.

Classes:
    None

Endpoints:
    GET /virtual-machines/:
        Retrieve all virtual machines.
    GET /virtual-machines/{vm_id}/:
        Retrieve a specific virtual machine by ID.
    POST /virtual-machines/create/:
        Create a new virtual machine.
    DELETE /virtual-machines/{vm_id}/:
        Delete a virtual machine by ID.
    POST /virtual-machines/{vm_id}/start/:
        Start a virtual machine by ID.
    POST /virtual-machines/{vm_id}/shut-off/:
        Shut off a virtual machine by ID.
    POST /virtual-machines/{vm_id}/edit/:
        Edit a virtual machine by ID.
    GET /virtual-machines/{vm_id}/vnc/:
        Access the VNC session of a virtual machine by ID.
    GET /virtual-machines/{vm_id}/snapshots/:
        Get a list of snapshots of virtual machine.
    GET /virtual-machines/{vm_id}/snapshots/{snap_id}/:
        Get an info about specific snapshot by ID.
    POST /virtual-machines/{vm_id}/snapshots/:
        Create a new snapshot of virtual machine.
    POST /virtual-machines/{vm_id}/snapshots/{snap_id}/revert/:
        Revert to snapshot of virtual machine.
    DELETE /virtual-machines/{vm_id}/snapshots/{snap_id}/:
        Delete a snapshot of virtual machine.
"""

from uuid import UUID
from typing import cast

from fastapi import Path, Depends, APIRouter, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.virtual_machines.entrypoints import schemas
from openvair.modules.virtual_machines.entrypoints.crud import VMCrud

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/virtual-machines',
    tags=['virtual-machine'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=Page[schemas.VirtualMachineInfo],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_vms(
    crud: VMCrud = Depends(VMCrud),
) -> Page[schemas.VirtualMachineInfo]:
    """Retrieve all virtual machines.

    Args:
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        Page[schemas.VirtualMachineInfo]: A paginated list of all virtual
        machines.
    """
    LOG.info('API handling request to get all virtual machines.')
    vms = await run_in_threadpool(crud.get_all_vms)
    LOG.info('API request was successfully processed.')
    return cast('Page', paginate(vms))


@router.get(
    '/{vm_id}/',
    response_model=schemas.VirtualMachineInfo,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_vm(
    vm_id: str = Path(description='VM ID'),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.VirtualMachineInfo:
    """Retrieve a virtual machine by ID.

    Args:
        vm_id (str): The ID of the virtual machine to retrieve.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.VirtualMachineInfo: The virtual machine data.
    """
    LOG.info(f'API handling request to get virtual machine with ID: {vm_id}.')
    vm = await run_in_threadpool(crud.get_vm, vm_id)
    LOG.info('API request was successfully processed.')
    return schemas.VirtualMachineInfo(**vm)


@router.post(
    '/create/',
    response_model=schemas.VirtualMachineInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_vm(
    data: schemas.CreateVirtualMachine,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.VirtualMachineInfo:
    """Create a new virtual machine.

    Args:
        data (schemas.CreateVirtualMachine): The data required to create a
            new virtual machine.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.VirtualMachineInfo: The created virtual machine data.
    """
    LOG.info('API handling request to create a new virtual machine.')
    vm = await run_in_threadpool(
        crud.create_vm, data.model_dump(mode='json'), user_info
    )
    LOG.info('API request was successfully processed.')
    return schemas.VirtualMachineInfo(**vm)


@router.delete(
    '/{vm_id}/',
    status_code=status.HTTP_201_CREATED,
)
async def delete_vm(
    vm_id: str,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> JSONResponse:
    """Delete a virtual machine by ID.

    Args:
        vm_id (str): The ID of the virtual machine to delete.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        JSONResponse: The response indicating the result of the deletion.
    """
    LOG.info(
        f'API handling request to delete virtual machine with ID: {vm_id}.'
    )
    vm = await run_in_threadpool(crud.delete_vm, vm_id, user_info)
    LOG.info('API request was successfully processed.')
    return JSONResponse(vm)


@router.post(
    '/{vm_id}/start/',
    response_model=schemas.VirtualMachineInfo,
    status_code=status.HTTP_201_CREATED,
)
async def start_vm(
    vm_id: str,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.VirtualMachineInfo:
    """Start a virtual machine by ID.

    Args:
        vm_id (str): The ID of the virtual machine to start.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.VirtualMachineInfo: The virtual machine data.
    """
    LOG.info(f'API handling request to start virtual machine with ID: {vm_id}.')
    vm = await run_in_threadpool(crud.start_vm, vm_id, user_info)
    LOG.info('API request was successfully processed.')
    return schemas.VirtualMachineInfo(**vm)


@router.post(
    '/{vm_id}/shut-off/',
    response_model=schemas.VirtualMachineInfo,
    status_code=status.HTTP_201_CREATED,
)
async def shut_off_vm(
    vm_id: str,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.VirtualMachineInfo:
    """Shut off a virtual machine by ID.

    Args:
        vm_id (str): The ID of the virtual machine to shut off.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.VirtualMachineInfo: The virtual machine data.
    """
    LOG.info(
        f'API handling request to shut off virtual machine with ID: {vm_id}.'
    )
    vm = await run_in_threadpool(crud.shut_off_vm, vm_id, user_info)
    LOG.info('API request was successfully processed.')
    return schemas.VirtualMachineInfo(**vm)


@router.post(
    '/{vm_id}/edit/',
    response_model=schemas.VirtualMachineInfo,
    status_code=status.HTTP_201_CREATED,
)
async def edit_vm(
    vm_id: str,
    data: schemas.EditVm,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.VirtualMachineInfo:
    """Edit a virtual machine by ID.

    Args:
        vm_id (str): The ID of the virtual machine to edit.
        data (schemas.EditVm): The data to update the virtual machine.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.VirtualMachineInfo: The updated virtual machine data.
    """
    LOG.info(f'API handling request to edit virtual machine with ID: {vm_id}.')
    vm = await run_in_threadpool(
        crud.edit_vm, vm_id, data.model_dump(mode='json'), user_info
    )
    LOG.info('API request was successfully processed.')
    return schemas.VirtualMachineInfo(**vm)


@router.get(
    '/{vm_id}/vnc/',
    response_model=schemas.Vnc,
    status_code=status.HTTP_200_OK,
)
async def vnc_vm(
    vm_id: str,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.Vnc:
    """Access the VNC session of a virtual machine by ID.

    Args:
        vm_id (str): The ID of the virtual machine.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.Vnc: The VNC session details.
    """
    result = await run_in_threadpool(crud.vnc, vm_id, user_info)
    return schemas.Vnc(**result)


@router.post(
    '/{vm_id}/clone/',
    response_model=list[schemas.VirtualMachineInfo],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def clone_vm(
    data: schemas.CloneVm,
    vm_id: str = Path(description='Id of vm that will be cloned'),
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> list[schemas.VirtualMachineInfo]:
    """Clone a virtual machine.

    Args:
        vm_id (str): The ID of the virtual machine to copy.
        data (schemas.CloneVm): The data to clone the virtual machine.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        List[schemas.VirtualMachineInfo]: The list of cloned virtual machine
    """
    LOG.info(
        f'API handling request to copy data for VM with ID: {vm_id} '
        f'{data.count} times.'
    )
    result: list[dict] = await run_in_threadpool(
        crud.clone_vm, vm_id, data.count, data.target_storage_id, user_info
    )
    LOG.info('API request was successfully processed.')
    return [schemas.VirtualMachineInfo(**item) for item in result]


@router.get(
    '/{vm_id}/snapshots/',
    response_model=schemas.ListOfSnapshots,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_snapshots(
    vm_id: UUID,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.ListOfSnapshots:
    """Retrieve all snapshots of the specific virtual machine.

    Args:
        vm_id (UUID): The ID of the virtual machine.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.ListOfSnapshots: A list of all snapshots of the specific
        virtual machine.
    """
    LOG.info(
        f'API handling request to get snapshots of '
        f'virtual machine with ID: {vm_id}.'
    )
    snapshots = await run_in_threadpool(
        crud.get_snapshots, str(vm_id), user_info
    )
    LOG.info('API request was successfully processed.')
    return schemas.ListOfSnapshots(snapshots=snapshots)


@router.get(
    '/{vm_id}/snapshots/{snap_id}',
    response_model=schemas.SnapshotInfo,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_snapshot(
    vm_id: UUID,
    snap_id: UUID,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.SnapshotInfo:
    """Retrieve a snapshot of a specific virtual machine by snapshot ID.

    Args:
        vm_id (UUID): The ID of the virtual machine.
        snap_id (UUID): The ID of the snapshot.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.SnapshotInfo: The snapshot data.
    """
    LOG.info(
        f'API handling request to get a snapshot with ID: {snap_id} '
        f'of virtual machine with ID: {vm_id}.'
    )
    snapshot = await run_in_threadpool(
        crud.get_snapshot, str(vm_id), str(snap_id), user_info
    )
    LOG.info('API request was successfully processed.')
    return schemas.SnapshotInfo(**snapshot)


@router.post(
    '/{vm_id}/snapshots/',
    response_model=schemas.SnapshotInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_snapshot(
    vm_id: UUID,
    data: schemas.CreateSnapshot,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.SnapshotInfo:
    """Create a new snapshot of the virtual machine.

    Args:
        vm_id (UUID): The ID of the virtual machine where the snapshot will be
        created.
        data (schemas.CreateSnapshot): The data required to create a new
        snapshot of the virtual machine.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        Dict: The created snapshot data.
    """
    LOG.info(
        f'API handling request to create a snapshot '
        f'of virtual machine with ID: {vm_id}.'
    )
    snapshot = await run_in_threadpool(
        crud.create_snapshot,
        str(vm_id),
        data.model_dump(mode='json'),
        user_info,
    )
    LOG.info('API request was successfully processed.')
    return schemas.SnapshotInfo(**snapshot)


@router.post(
    '/{vm_id}/snapshots/{snap_id}/revert',
    response_model=schemas.SnapshotInfo,
    status_code=status.HTTP_200_OK,
)
async def revert_snapshot(
    vm_id: UUID,
    snap_id: UUID,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.SnapshotInfo:
    """Revert a virtual machine to a snapshot.

    Args:
        vm_id (UUID): The ID of the virtual machine where the snapshot will be
        reverted.
        snap_id (UUID): The ID of the snapshot to revert.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.SnapshotInfo: The reverted snapshot data.
    """
    LOG.info(
        f'API handling request to revert snapshot (ID: {snap_id}) '
        f'of virtual machine with ID: {vm_id}'
    )
    snapshot = await run_in_threadpool(
        crud.revert_snapshot, str(vm_id), str(snap_id), user_info
    )
    LOG.info('API request was successfully processed.')
    return schemas.SnapshotInfo(**snapshot)


@router.delete(
    '/{vm_id}/snapshots/{snap_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_snapshot(
    vm_id: UUID,
    snap_id: UUID,
    user_info: dict = Depends(get_current_user),
    crud: VMCrud = Depends(VMCrud),
) -> schemas.SnapshotInfo:
    """Delete a snapshot of virtual machine.

    Args:
        vm_id (UUID): The ID of the virtual machine where snapshot will be
        deleted.
        snap_id (UUID): The ID of the snapshot to delete.
        user_info (Dict): The dependency to ensure the user is authenticated.
        crud (VMCrud): The CRUD dependency for virtual machine operations.

    Returns:
        schemas.SnapshotInfo: The deleted snapshot data.
    """
    LOG.info(
        f'API handling request to delete snapshot (ID: {snap_id}) '
        f'from virtual machine with ID: {vm_id}.'
    )
    snapshot = await run_in_threadpool(
        crud.delete_snapshot, str(vm_id), str(snap_id), user_info
    )
    LOG.info('API request was successfully processed.')
    return schemas.SnapshotInfo(**snapshot)
