"""Authentication endpoints.

This module defines the API routes for user authentication, including endpoints
for obtaining access tokens and refreshing existing tokens. It uses FastAPI
to handle requests and responses and integrates with the UserCrud class for
user authentication and token management.

Endpoints:
    - POST /auth/ - Authenticate a user and return tokens.
    - POST /auth/refresh - Refresh an access token using a refresh token.

Dependencies:
    - HTTPBearer: Security scheme for handling authentication tokens.
    - UserCrud: Class for user-related CRUD operations.
    - OAuth2PasswordRequestForm: Form data for user authentication.
    - JWT utilities: For creating and verifying JWT tokens.
"""

from typing import Any, Dict

import jwt
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import (
    create_tokens,
    create_access_token,
    create_refresh_token,
)
from openvair.modules.user.config import ALGORITHM, JWT_SECRET, TOKEN_TYPE
from openvair.modules.user.entrypoints import schemas
from openvair.modules.user.entrypoints.crud import UserCrud

LOG = get_logger(__name__)
http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {'description': 'Not found!'}},
)


@router.post(
    '/',
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
)
def auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    crud: UserCrud = Depends(UserCrud),
) -> Dict:
    """Authenticate a user and return access and refresh tokens.

    Args:
        form_data: The form data containing username and password.
        crud: UserCrud instance for performing CRUD operations.

    Returns:
       Dict: A dictionary containing access and refresh tokens and
            the token type.
    """
    LOG.info('Api start user authentication.')
    user: Dict = crud.auth(form_data.username, form_data.password)
    tokens: Dict = create_tokens(user)
    LOG.info('Api request was successfully processed.')
    return tokens


@router.post(
    '/refresh',
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
)
def refresh_token(refresh_token: str) -> Dict:
    """Refresh an access token using a refresh token.

    Args:
        refresh_token: The refresh token provided by the user.

    Returns:
       Dict: A dictionary containing the new access token, refresh token,
            and token type.

    Raises:
        HTTPException: If the refresh token is expired or invalid.
    """
    try:
        payload = jwt.decode(
            refresh_token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
        )

        user: Dict[Any, Any] = {
            k: v for k, v in payload.items() if k not in ('exp', 'type')
        }

        new_refresh_token: str = create_refresh_token(user)
        new_access_token: str = create_access_token(user)
    except jwt.ExpiredSignatureError:
        LOG.warning('Refresh token expired')
        raise HTTPException(status_code=401, detail='Refresh token expired')
    except jwt.InvalidTokenError:
        LOG.error('Invalid refresh token')
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    else:
        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': TOKEN_TYPE,
        }
