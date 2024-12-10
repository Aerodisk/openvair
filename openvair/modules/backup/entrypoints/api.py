"""Module providing API endpoints for managing backups."""

from fastapi import APIRouter

router = APIRouter(
    prefix='/backup',
    tags=['backup'],
    responses={404: {'description': 'Not found!'}},
)
