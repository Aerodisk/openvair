"""API entrypoint for template management.

This module defines the API routes for managing templates.

Router:
    - Prefix: `/templates`
    - Tags: `template`
    - Responses: `{404: 'Not found!'}`

Dependencies:
    - FastAPI APIRouter: Handles API routing.
    - Logging: Provides structured logging for API events.
"""

from fastapi import APIRouter

from openvair.libs.log import get_logger

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/templates',
    tags=['template'],
    responses={404: {'description': 'Not found!'}},
)
