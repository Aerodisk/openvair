"""Module providing API endpoints for managing block device interfaces.

This module defines several API endpoints for managing block device interfaces,
such as iSCSI and Fibre Channel. The endpoints allow users to perform various
operations, including retrieving sessions, getting the host IQN, logging in and
out of iSCSI targets, and performing a LIP (Loop Initialization Procedure)
scan on Fibre Channel host adapters.

The module uses the FastAPI framework to define the API routes and handle the
requests. It also utilizes the `InterfaceCrud` class from the
`openvair.modules.block_device.entrypoints.crud` module to perform the
necessary CRUD (Create, Read, Update, Delete) operations on the block device
interfaces.

The module includes several Pydantic data models defined in the
`openvair.modules.block_device.entrypoints.schemas` module, which are used to
represent the various types of block device interfaces and their associated
data.

Routes:
    /block-devices/sessions: Retrieve sessions associated with block devices.
    /block-devices/get-iqn: Get the IQN associated with the current host.
    /block-devices/login: Log in to the specified iSCSI target.
    /block-devices/logout: Log out from the specified iSCSI target.
    /block-devices/lip_scan: Perform a LIP scan on Fibre Channel host adapters.
"""

from typing import Dict, List

from fastapi import Depends, APIRouter, status
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import regex_matcher, get_current_user
from openvair.modules.block_device.entrypoints import schemas
from openvair.modules.block_device.entrypoints.crud import InterfaceCrud

LOG = get_logger(__name__)
UUID_REGEX = regex_matcher('uuid4')

router = APIRouter(
    prefix='/block-devices',
    tags=['block-devices'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/sessions',
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_sessions(
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> List[schemas.Session]:
    """Retrieve sessions associated with block devices.

    Args:
        crud (InterfaceCrud, optional): An instance of the `InterfaceCrud`
            interface that provides access to the database.
            Defaults to `Depends(InterfaceCrud)`.

    Returns:
        List[schemas.Session]: A list of schemas.Session representing the
            sessions. Each object contains information about a session

    Raises:
        HTTPException: If there is an error while retrieving the sessions, it
            raises an HTTPException with an appropriate status code and error
            message.
    """
    LOG.info('Api request start getting sessions.')
    result = await run_in_threadpool(crud.get_sessions)
    LOG.info('Api request for getting sessions was successfully processed.')
    return [schemas.Session(**session) for session in result]


@router.get(
    '/get-iqn',
    response_model=schemas.IQN,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
    ],
)
async def get_host_iqn(
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> schemas.IQN:
    """Gets the IQN associated with the current host.

    Args:
        crud (InterfaceCrud, optional): An instance of the `InterfaceCrud`
            interface that provides access to the necessary data.
            Defaults to `Depends(InterfaceCrud)`.

    Returns:
        schemas.IQN: A `schemas.IQN` object containing the IQN associated with
            the current host.

    Raises:
        HTTPException: If there is an error while retrieving the host IQN, this
            function raises an `HTTPException` with an appropriate status code
            and error message.
    """
    LOG.info('Api request start getting host iqn.')
    result = await run_in_threadpool(crud.get_host_iqn)
    LOG.info('Api request for getting host iqn was successfully processed.')
    return schemas.IQN(**result)


@router.post(
    '/login',
    response_model=schemas.InterfaceLogin,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
    ],
)
async def login(
    data: schemas.Interface,
    user_data: Dict = Depends(get_current_user),
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> schemas.InterfaceLogin:
    """Log in to the specified iSCSI target.

    Args:
        data (schemas.Interface): The data required for the login operation,
            such as target details, authentication credentials, etc.
        user_data (Dict, optional): Additional user data to be included in the
            request.
            Defaults to `Depends(get_current_user)`.
        crud (InterfaceCrud, optional): An instance of the `InterfaceCrud`
            interface that provides access to the necessary data for the login
            operation. Defaults to `Depends(InterfaceCrud)`.

    Returns:
        schemas.InterfaceLogin: A `schemas.InterfaceLogin` object containing the
            result of the login operation.

    Raises:
        HTTPException: If there is an error while logging in to the iSCSI
            target, this function raises an `HTTPException` with an appropriate
            status code and error message.
    """
    LOG.info('Api request start login to interface of block device.')
    result = await run_in_threadpool(crud.login, data.dict(), user_data)
    LOG.info(
        'Api request for login to interface of block device was successfully'
        'processed.'
    )
    return schemas.InterfaceLogin(**result)


@router.post(
    '/logout',
    response_model=schemas.InterfaceDeleted,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
    ],
)
async def logout(
    data: schemas.InterfaceDeleted,
    user_data: Dict = Depends(get_current_user),
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> schemas.InterfaceDeleted:
    """Log out from the specified iSCSI target.

    Args:
        data (schemas.InterfaceDeleted): The data required for the logout
            operation.
        user_data (Dict, optional): Additional user data to be included in the
            request. Defaults to Depends(get_current_user).
        crud (InterfaceCrud, optional): The InterfaceCrud instance to use for
            the logout operation. Defaults to Depends(InterfaceCrud).

    Returns:
        schemas.InterfaceDeleted: The result of the logout operation.
    """
    LOG.info('Api request start logout from interface of block device.')
    result = await run_in_threadpool(crud.logout, data.dict(), user_data)
    LOG.info(
        'Api request for logout from interface of block device was successfully'
        'processed.'
    )
    return schemas.InterfaceDeleted(**result)


@router.get(
    '/lip_scan',
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
    ],
)
async def lip_scan(
    crud: InterfaceCrud = Depends(InterfaceCrud),
) -> str:
    """Perform LIP scan on Fibre Channel host adapters.

    LIP - Loop Initialization Protocol

    Args:
        crud (InterfaceCrud, optional): An instance of the `InterfaceCrud`
            interface that provides access to the necessary functionality for
            performing the LIP scan.
            Defaults to `Depends(InterfaceCrud)`.

    Returns:
        str: A message about the result of the LIP scan.

    Raises:
        OSError: If there is an error accessing or writing to the 'issue_lip'
            file while performing the LIP scan.
    """
    LOG.info('Api request start lip_scan for block devices.')
    result = await run_in_threadpool(crud.lip_scan)
    LOG.info(
        'Api request for lip_scan for block device was successfully processed.'
    )
    return str(result)
