"""API endpoints for user management.

This module defines the API routes for user management, including endpoints
for retrieving user information, creating users, deleting users, and
changing user passwords. It uses FastAPI to handle requests and responses,
and integrates with the UserCrud class to perform the necessary operations.

Endpoints:
    - GET /user/ - Retrieve information for the current authenticated user.
    - POST /user/{user_id}/create/ - Create a new user.
    - DELETE /user/{user_id}/ - Delete a user by ID.
    - POST /user/{user_id}/change-password/ - Change the password for a user.

Dependencies:
    - HTTPBearer: Security scheme for handling authentication tokens.
    - UserCrud: Class for user-related CRUD operations.
    - get_current_user: Dependency for retrieving the current authenticated
        user.
"""

from typing import Dict

from fastapi import Path, Depends, APIRouter, status
from fastapi.security import HTTPBearer

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import get_current_user
from openvair.modules.user.entrypoints import schemas
from openvair.libs.validation.validators import regex_matcher
from openvair.modules.user.entrypoints.crud import UserCrud

LOG = get_logger(__name__)
UUID_REGEX: str = regex_matcher('uuid4')

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix='/user',
    tags=['user'],
    responses={404: {'description': 'Not found!'}},
    dependencies=[Depends(http_bearer)],
)


@router.get(
    '/',
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
)
def get_user(
    crud: UserCrud = Depends(UserCrud),
    user_dict: Dict = Depends(get_current_user),
) -> schemas.User:
    """Retrieve current authenticated user information.

    Args:
        crud: UserCrud instance for performing CRUD operations.
        user_dict: Dictionary containing current authenticated user data.

    Returns:
        schemas.User: The current authenticated user's information.
    """
    LOG.info('Api start getting current user info.')
    user: Dict = crud.get_user(user_dict.get('id', ''))
    LOG.info('Api request was successfully processed.')
    return schemas.User(**user)


@router.post(
    '/{user_id}/create/',
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: schemas.UserCreate,
    user_id: str = Path(..., regex=UUID_REGEX),
    user_data: Dict = Depends(get_current_user),
    crud: UserCrud = Depends(UserCrud),
) -> schemas.User:
    """Create a new user and return the user's credentials.

    Args:
        data: User creation data including username, password, and email.
        user_id: The ID of the current user (must be a superuser to create
            new users).
        user_data: Current authenticated user data.
        crud: UserCrud instance for performing CRUD operations.

    Returns:
        schemas.User: The created user's credentials.
    """
    LOG.info('Api start creating user.')
    user: Dict = crud.create_user(data.dict(), user_id, user_data)
    LOG.info('Api request was successfully processed.')
    return schemas.User(**user)


@router.delete(
    '/{user_id}/',
    response_model=schemas.UserDelete,
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: str = Path(..., regex=UUID_REGEX),
    user_data: Dict = Depends(get_current_user),
    crud: UserCrud = Depends(UserCrud),
) -> schemas.UserDelete:
    """Delete a user from the database.

    Args:
        user_id: The ID of the user to be deleted.
        user_data: Current authenticated user data.
        crud: UserCrud instance for performing CRUD operations.

    Returns:
        schemas.UserDelete: Result of the delete operation.
    """
    LOG.info('Api start deleting user.')
    result: Dict = crud.delete_user(user_id, user_data)
    LOG.info('Api request was successfully processed.')
    return schemas.UserDelete(**result)


@router.post(
    '/{user_id}/change-password/',
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
    ],
)
def change_password(
    data: schemas.UserChangePassword,
    user_id: str = Path(..., regex=UUID_REGEX),
    crud: UserCrud = Depends(UserCrud),
) -> schemas.User:
    """Change the password for a user.

    Args:
        data: New password data.
        user_id: The ID of the user whose password is to be changed.
        crud: UserCrud instance for performing CRUD operations.

    Returns:
        schemas.User: The user's updated information after changing the
            password.
    """
    LOG.info('Api start changing user password.')
    result: Dict = crud.change_password(user_id, data.dict())
    LOG.info('Api request was successfully processed.')
    return schemas.User(**result)
