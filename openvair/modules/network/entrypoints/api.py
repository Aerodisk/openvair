"""API endpoints for managing network interfaces and bridges.

This module provides API routes for retrieving, creating, updating, and
deleting network interfaces and bridges. It uses FastAPI for defining
endpoints and managing requests.

Routes:
    - GET /interfaces: Retrieve a list of all interfaces.
    - GET /interfaces/bridges: Retrieve the list of network bridges.
    - GET /interfaces/{iface_id}: Retrieve data for a specific interface.
    - POST /interfaces/create: Create a new network bridge.
    - DELETE /interfaces/delete: Delete a network bridge.
    - PUT /interfaces/{name}/turn_on: Turn on a specific interface.
    - PUT /interfaces/{name}/turn_off: Turn off a specific interface.
"""

from typing import Dict, List, cast

from fastapi import Path, Query, Depends, APIRouter, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import get_current_user
from openvair.libs.validation.validators import regex_matcher
from openvair.modules.network.entrypoints import schemas
from openvair.modules.network.entrypoints.crud import InterfaceCrud

LOG = get_logger(__name__)
UUID_REGEX = regex_matcher('uuid4')

router = APIRouter(
    prefix='/interfaces',
    tags=['interface'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=Page[schemas.Interface],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_interfaces(
    crud: InterfaceCrud = Depends(InterfaceCrud),
    *,
    is_need_filter: bool = Query(
        default=False, description='Flag for filtering interfaces.'
    ),
) -> Page[schemas.Interface]:
    """API endpoint for retrieving a list of all interfaces.

    Args:
        is_need_filter (Optional[bool], optional): Flag indicating whether to
            apply filtering on interfaces. Defaults to False.
        crud (InterfaceCrud, optional): Dependency injection for CRUD operations
            on interfaces.

    Returns:
        Page[schemas.Interface]: A paginated list of interfaces retrieved from
            the database.

    Raises:
        Exception: Any error that occurs during the process.
    """
    LOG.info('API: Start getting list of interfaces')
    interfaces = await run_in_threadpool(
        crud.get_all_interfaces, is_need_filter=is_need_filter
    )
    LOG.info('API: Request processed successfully.')
    return cast(Page, paginate(interfaces))


@router.get(
    '/bridges/',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_bridges_list(
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> List[Dict]:
    """API endpoint for retrieving the list of network bridges.

    Args:
        crud (InterfaceCrud, optional): Dependency injection for CRUD operations
            on interfaces.

    Returns:
        List[str]: A list of network bridges.

    Raises:
        Exception: Any error that occurs during the process.
    """
    LOG.info('API: Start retrieving network bridges')
    bridges_list = await run_in_threadpool(crud.get_bridges_list)
    LOG.info('API: Request processed successfully.')
    return bridges_list


@router.get(
    '/{iface_id}/',
    dependencies=[Depends(get_current_user)],
)
async def get_interface(
    iface_id: str = Path(
        ...,
        description='Interface ID (UUID4)',
        regex=UUID_REGEX,
    ),
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> schemas.Interface:
    """API endpoint for retrieving current network interface data.

    Args:
        iface_id (str): Interface ID (UUID4).
        crud (InterfaceCrud, optional): Dependency injection for CRUD operations
            on interfaces.

    Returns:
        schemas.Interface: Response containing information about the specified
            network interface.

    Raises:
        Exception: Any error that occurs during the process.
    """
    LOG.info('API: Start retrieving current network interface data')
    interface = await run_in_threadpool(crud.get_interface, iface_id)
    LOG.info('API: Request processed successfully.')
    return schemas.Interface(**interface)


@router.post(
    '/create/',
    response_model=schemas.BridgeCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bridge_create(
    data: schemas.BridgeCreate,
    user_info: Dict = Depends(get_current_user),
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> schemas.BridgeCreateResponse:
    """API endpoint for creating a network bridge.

    Args:
        data (schemas.BridgeCreate): Information about the bridge to be created.
        user_info (Dict): User information retrieved from the authentication
            token.
        crud (InterfaceCrud, optional): Dependency injection for CRUD operations
            on interfaces.

    Returns:
        schemas.BridgeCreateResponse: Response containing information about the
            created bridge.

    Raises:
        Exception: Any error that occurs during the process.
    """
    LOG.info('API: Start creating a network bridge')
    bridge = await run_in_threadpool(crud.create_bridge, data.dict(), user_info)
    LOG.info('API: Request processed successfully.')
    return schemas.BridgeCreateResponse(**bridge)


@router.delete(
    '/delete/',
    status_code=status.HTTP_202_ACCEPTED,
)
async def bridge_delete(
    data: schemas.BridgeDelete,
    user_info: Dict = Depends(get_current_user),
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> List[Dict]:
    """API endpoint for deleting a bridge.

    Args:
        data (schemas.BridgeDelete): Information about the bridge to delete.
        user_info (Dict): User information retrieved from the authentication
            token.
        crud (InterfaceCrud, optional): Dependency injection for CRUD operations
            on interfaces.

    Returns:
        List[Dict]: A list of responses containing information about the deleted
            bridges.

    Raises:
        Exception: Any error that occurs during the process.
    """
    LOG.info('API: Start deleting a bridge')
    bridge = await run_in_threadpool(
        crud.delete_bridge, data.dict().get('data', {}), user_info
    )
    LOG.info('API: Request processed successfully.')
    return bridge


@router.put(
    '/{name}/turn_on',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def turn_on_interface(
    name: str, crud: InterfaceCrud = Depends(InterfaceCrud)
) -> JSONResponse:
    """Turn on the specified interface.

    This function sends a turn-on command for the specified network interface
    via the provided CRUD operations. The actual operation is run in a thread
    pool to avoid blocking the event loop.

    Args:
        name (str): The name of the network interface to be turned on.
        crud (InterfaceCrud, optional): The CRUD operations dependency for
            managing interfaces.

    Returns:
        JSONResponse: A JSON response with a success message and HTTP 200
            status.
    """
    LOG.info(f'API: Turning on interface: {name}')

    await run_in_threadpool(
        crud.turn_on_interface,
        name,
    )

    message = f'API: Interface {name} turn on command was sent.'
    LOG.info(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)


@router.put(
    '/{name}/turn_off',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def turn_off_interface(
    name: str, crud: InterfaceCrud = Depends(InterfaceCrud)
) -> JSONResponse:
    """Turn off the specified interface.

    This function sends a turn-off command for the specified network interface
    via the provided CRUD operations. The actual operation is run in a thread
    pool to avoid blocking the event loop.

    Args:
        name (str): The name of the network interface to be turned off.
        crud (InterfaceCrud, optional): The CRUD operations dependency for
            managing interfaces.

    Returns:
        JSONResponse: A JSON response with a success message and HTTP 200
            status.
    """
    LOG.info(f'API: Turning off interface: {name}')

    await run_in_threadpool(
        crud.turn_off_interface,
        name,
    )

    message = f'API: Interface {name} turn off command was sent.'
    LOG.info(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)
