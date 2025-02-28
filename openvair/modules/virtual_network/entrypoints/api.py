"""API endpoints for managing virtual networks.

This module defines the API routes for virtual network management, including
endpoints for retrieving, creating, updating, and deleting virtual networks
and their associated port groups. It uses FastAPI to handle requests and
responses, and integrates with the VirtualNetworkCrud class to perform the
necessary operations.

Endpoints:
    - GET /virtual_networks/ - Retrieve a list of virtual networks.
    - GET /virtual_networks/{virtual_network_id}/ - Retrieve a virtual network
        by its ID.
    - GET /virtual_networks/{virtual_network_name} - Retrieve a virtual
        network by its name.
    - POST /virtual_networks/create/ - Create a new virtual network.
    - DELETE /virtual_networks/{virtual_network_id} - Delete a virtual network
        by its ID.
    - PUT /virtual_networks/{virtual_network_id}/turn_on - Turn on a virtual
        network by its ID.
    - PUT /virtual_networks/{virtual_network_id}/turn_off - Turn off a virtual
        network by its ID.
    - POST /virtual_networks/{virtual_network_id}/add_port_group - Add a port
        group to a virtual network.
    - DELETE /virtual_networks/{virtual_network_id}/delete_port_group - Delete
        a port group from a virtual network.
    - POST /virtual_networks/{virtual_network_id}/{port_group_name}/{trunk_id}/add_tag_id -
        Add a tag to a trunk port group in a virtual network.

Dependencies:
    - get_current_user: Dependency for retrieving the current authenticated
        user.
    - VirtualNetworkCrud: Class for performing CRUD operations on virtual
        networks.
"""  # noqa: E501, W505

from uuid import UUID
from typing import Dict

from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import get_current_user
from openvair.modules.virtual_network.entrypoints import schemas
from openvair.modules.virtual_network.entrypoints.crud import VirtualNetworkCrud

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/virtual_networks',
    tags=['virtual_network'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=schemas.ListOfVirtualNetworksResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {'model': schemas.ErrorResponseModel}},
)
async def get_virtual_networks(
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> schemas.ListOfVirtualNetworksResponse:
    """Retrieves a list of virtual networks.

    Args:
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        ListOfVirtualNetworksResponse: A list of virtual networks.

    Responses:
        200: Successful request. Returns a list of virtual networks.
        400: Request error. Returns an ErrorResponseModel.
    """
    LOG.info('Api start getting list of virtual networks')

    virtual_networks = await run_in_threadpool(crud.get_all_virtual_networks)

    LOG.info('Api request was successfully processed.')
    return schemas.ListOfVirtualNetworksResponse(**virtual_networks)


@router.get(
    '/{virtual_network_id}/',
    response_model=schemas.VirtualNetworkResponse,
    responses={400: {'model': schemas.ErrorResponseModel}},
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_virtual_network_by_id(
    virtual_network_id: UUID,
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> schemas.VirtualNetworkResponse:
    """Retrieves a virtual network by its ID.

    Args:
        virtual_network_id (str): The ID of the virtual network.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        VirtualNetworkResponse: The virtual network corresponding to the
        provided ID.

    Responses:
        200: Successful request. Returns the virtual network.
        400: Request error. Returns an ErrorResponseModel.
    """
    LOG.info(f'Api start getting virtual network by id: {virtual_network_id}')

    virtual_network = await run_in_threadpool(
        crud.get_virtual_network_by_id,
        virtual_network_id,
    )

    LOG.info('Api request was successfully processed.')
    return schemas.VirtualNetworkResponse(**virtual_network)


@router.get(
    '/{virtual_network_name}',
    response_model=schemas.VirtualNetworkResponse,
    responses={400: {'model': schemas.ErrorResponseModel}},
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_virtual_network_by_name(
    virtual_network_name: str,
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> schemas.VirtualNetworkResponse:
    """Retrieves a virtual network by its name.

    Args:
        virtual_network_name (str): The name of the virtual network.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        VirtualNetworkResponse: The virtual network corresponding to the
        provided name.

    Responses:
        200: Successful request. Returns the virtual network.
        400: Request error. Returns an ErrorResponseModel.
    """
    LOG.info(
        f'Api start getting virtual network by name {virtual_network_name}'
    )

    virtual_network = await run_in_threadpool(
        crud.get_virtual_network_by_name,
        virtual_network_name,
    )

    LOG.info('Api request was successfully processed.')
    return schemas.VirtualNetworkResponse(**virtual_network)


@router.post(
    '/create/',
    response_model=schemas.VirtualNetworkResponse,
    responses={400: {'model': schemas.ErrorResponseModel}},
    status_code=status.HTTP_200_OK,
)
async def create_virtual_network(
    data: schemas.VirtualNetwork,
    user_info: Dict = Depends(get_current_user),
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> schemas.VirtualNetworkResponse:
    """Creates a new virtual network.

    Args:
        data (schemas.VirtualNetwork): Data representing the virtual network
            to be created.
        user_info: User information injected by FastAPI.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        VirtualNetworkResponse: The newly created virtual network.

    Responses:
        200: Successful request. Returns the newly created virtual network.
        400: Request error. Returns an ErrorResponseModel.
    """
    LOG.info('Api start creating virtual network')

    virtual_network = await run_in_threadpool(
        crud.create_virtual_network,
        data,
        user_info,
    )

    LOG.info('Api request was successfully processed.')
    return schemas.VirtualNetworkResponse(**virtual_network)


@router.delete(
    '/{virtual_network_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_virtual_network(
    virtual_network_id: UUID,
    user_info: Dict = Depends(get_current_user),
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> JSONResponse:
    """Deletes a virtual network by its ID.

    Args:
        virtual_network_id (str): The ID of the virtual network to be deleted.
        user_info: User information injected by FastAPI.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        JSONResponse: A message indicating the success of the delete operation.

    Responses:
        200: Successful request. Returns a message indicating the success of
        the delete operation.
    """
    LOG.info(
        f'Api starting deleting virtual network by id: {virtual_network_id}'
    )

    await run_in_threadpool(
        crud.delete_virtual_network,
        virtual_network_id,
        user_info,
    )

    message = (
        f'Deleting command was successful send for '
        f'Virtual network {virtual_network_id}'
    )
    LOG.info(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)


@router.put(
    '/{virtual_network_id}/turn_on',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def turn_on_virtual_network(
    virtual_network_id: str,
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> JSONResponse:
    """Turns on a virtual network identified by its ID.

    Args:
        virtual_network_id (str): The ID of the virtual network to be turned on.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        JSONResponse: A message indicating the success of the turn-on operation.

    Responses:
        200: Successful request. Returns a message indicating the success of
        the turn-on operation.
    """
    LOG.info(f'Api turn_on virtual network: {virtual_network_id}')

    await run_in_threadpool(
        crud.turn_on_virtual_network,
        virtual_network_id,
    )

    message = (
        f'Api Virtual network {virtual_network_id} turn on command was sent.'
    )
    LOG.info(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)


@router.put(
    '/{virtual_network_id}/turn_off',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def turn_off_virtual_network(
    virtual_network_id: str,
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> JSONResponse:
    """Turns off a virtual network identified by its ID.

    Args:
        virtual_network_id (str): The ID of the virtual network to be turned
            off.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        JSONResponse: A message indicating the success of the turn-off operation

    Responses:
        200: Successful request. Returns a message indicating the success of
        the turn-off operation.
    """
    LOG.info(f'Api turn_off virtual network: {virtual_network_id}')

    await run_in_threadpool(
        crud.turn_off_virtual_network,
        virtual_network_id,
    )

    message = (
        f'Api Virtual network {virtual_network_id} turn off command was sent.'
    )
    LOG.info(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)


@router.post(
    '/{virtual_network_id}/add_port_group',
    status_code=status.HTTP_200_OK,
    response_model=schemas.VirtualNetworkResponse,
)
async def add_port_group(
    virtual_network_id: str,
    port_group: schemas.PortGroup,
    user_info: Dict = Depends(get_current_user),
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> schemas.VirtualNetworkResponse:
    """Adds a port group to a virtual network.

    Args:
        virtual_network_id (str): The ID of the virtual network to which the
            port group will be added.
        port_group (schemas.PortGroup): The port group data to be added.
        user_info: User information injected by FastAPI.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        VirtualNetworkResponse: The virtual network with the added port group.

    Responses:
        200: Successful request. Returns the virtual network with the added port
        group.
    """
    LOG.info(
        f'Api handle response on adding port_group to {virtual_network_id}'
    )

    result = await run_in_threadpool(
        crud.add_port_group,
        virtual_network_id,
        port_group,
        user_info,
    )

    LOG.info('Api request was successfully processed.')
    return schemas.VirtualNetworkResponse(**result)


@router.delete(
    '/{virtual_network_id}/delete_port_group',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def delete_port_group(
    virtual_network_id: str,
    port_group_name: str,
    user_info: Dict = Depends(get_current_user),
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> JSONResponse:
    """Deletes a port group from a virtual network.

    Args:
        virtual_network_id (str): The ID of the virtual network from which the
            port group will be deleted.
        port_group_name (str): The name of the port group to be deleted.
        user_info: User information injected by FastAPI.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        JSONResponse: A message indicating the success of the delete operation.

    Responses:
        200: Successful request. Returns a message indicating the success of the
        delete operation.
    """
    LOG.info(
        f'Api handle response on deleting port_group to {virtual_network_id}'
    )

    await run_in_threadpool(
        crud.delete_port_group,
        virtual_network_id,
        port_group_name,
        user_info,
    )

    message = 'Delete port group command was sent.'
    LOG.info(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)


@router.post(
    '/{virtual_network_id}/{port_group_name}/{trunk_id}/add_tag_id',
    status_code=status.HTTP_200_OK,
    response_model=schemas.PortGroup,
)
async def add_tag_to_trunk_port_group(
    virtual_network_id: str,
    port_group_name: str,
    tag_id: str,
    user_info: Dict = Depends(get_current_user),
    crud: VirtualNetworkCrud = Depends(VirtualNetworkCrud),
) -> schemas.PortGroup:
    """Adds a tag to a trunk port group in a virtual network.

    Args:
        virtual_network_id (str): The ID of the virtual network.
        port_group_name (str): The name of the port group.
        tag_id (str): The tag ID to be added to the port group.
        user_info: User information injected by FastAPI.
        crud: VirtualNetworkCrud instance injected by FastAPI.

    Returns:
        PortGroup: The updated port group with the added tag.

    Responses:
        200: Successful request. Returns the updated port group.
    """
    LOG.info('Api adding tag to trunk port_group')

    result = await run_in_threadpool(
        crud.add_tag_to_trunk_port_group,
        virtual_network_id,
        port_group_name,
        tag_id,
        user_info,
    )

    LOG.info('Api request was successfully processed.')
    return schemas.PortGroup(**result)
