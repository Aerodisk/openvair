"""Need to write"""

from typing import Dict, Optional
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Depends, HTTPException, security

from openvair import config
from openvair.libs.log import get_logger

oauth2schema = security.OAuth2PasswordBearer('/auth/')
JWT_SECRET = config.data['jwt'].get('secret')
TOKEN_TYPE = config.data['jwt'].get('token_type')
ALGORITHM = config.data['jwt'].get('algorithm')
ACCESS_TOKEN_EXPIRE_MINUTES = config.data['jwt'].get(
    'access_token_expiration_minutes', 30
)
REFRESH_TOKEN_EXPIRATION_DAYS = config.data['jwt'].get(
    'refresh_token_expiration_days', 7
)
LOG = get_logger(__name__)


def get_current_user(token: str = Depends(oauth2schema)) -> Dict:
    """Retrieves the current user from a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Dict: The user object decoded from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload: Dict = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[
                ALGORITHM,
            ],
        )

        if payload['type'] != 'access':
            raise HTTPException(status_code=401, detail='Invalid access token')

        payload.update({'token': token})
        LOG.info(f'User authenticated: {payload["username"]}')
    except jwt.ExpiredSignatureError:
        LOG.error('Token expired')
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        LOG.error('Invalid token')
        raise HTTPException(status_code=401, detail='Invalid token')
    else:
        return payload


def create_access_token(user: Dict, ttl_minutes: Optional[int] = None) -> str:
    """Creates a JWT access token.

    Args:
        user (Dict): The user object to encode in the token.
        ttl_minutes (Optional[int]): The time-to-live (TTL) for the token in
            minutes.

    Returns:
        str: The encoded access token.

    Raises:
        HTTPException: If token creation fails.
    """
    try:
        payload = user.copy()
        LOG.info(f'Start creating access token with payload: {payload}')

        # Use timedelta to add the TTL to the current time
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ttl_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload.update({'exp': expire, 'type': 'access'})

        token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=ALGORITHM)
        LOG.info(f'Created access token data: {token}')

    except jwt.PyJWTError as error:
        LOG.error(f'Access token creation failed: {error}')
        raise HTTPException(
            status_code=400, detail='Invalid username or password'
        )
    else:
        return token


def create_refresh_token(user: Dict, ttl_days: Optional[int] = None) -> str:
    """Creates a JWT refresh token.

    Args:
        user (Dict): The user object to encode in the token.
        ttl_days (Optional[int]): The time-to-live (TTL) for the refresh token
            in days.

    Returns:
        str: The encoded refresh token.

    Raises:
        HTTPException: If token creation fails.
    """
    try:
        payload = user.copy()
        LOG.info(f'Start creating refresh token with payload: {payload}')

        # Use timedelta to add the TTL to the current time
        expire = datetime.now(timezone.utc) + timedelta(
            days=ttl_days or REFRESH_TOKEN_EXPIRATION_DAYS
        )

        payload.update({'exp': expire, 'type': 'refresh'})

        token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=ALGORITHM)
        LOG.info(f'Created refresh token data: {token}')
    except jwt.PyJWTError as error:
        LOG.error(f'Refresh token creation failed: {error}')
        raise HTTPException(
            status_code=400, detail='Invalid username or password'
        )
    else:
        return token


def create_tokens(user: Dict) -> Dict:
    """Creates a dictionary containing access and refresh tokens.

    Args:
        user (Dict): The user object to encode in the tokens.

    Returns:
        Dict: A dictionary containing the access and refresh tokens.
    """
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': TOKEN_TYPE,
    }
