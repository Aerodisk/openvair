"""Module for handling event-related API endpoints.

This module defines the FastAPI router and endpoint for retrieving events.
It uses the `EventCrud` class for database interactions and includes user
authentication dependencies.

Attributes:
    LOG (Logger): Logger instance for logging events in the module.
    router (APIRouter): FastAPI router for event-related endpoints.
"""

import io
import csv
from typing import Dict, List, cast

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi_pagination import Page, Params, paginate
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.event_store.entrypoints import schemas
from openvair.modules.event_store.entrypoints.crud import EventCrud

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/event',
    tags=['event'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=Page[schemas.Event],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_events(
    crud: EventCrud = Depends(EventCrud),
) -> Page[schemas.Event]:
    """Retrieve all events from the database.

    This endpoint retrieves all events using the EventCrud class and returns
    them in a paginated format.

    Args:
        crud (EventCrud): Instance of EventCrud for database operations.

    Returns:
        Page[schemas.Event]: A paginated list of events.

    Raises:
        HTTPException: If any database error occurs or events are not found.
    """
    result: List = crud.get_all_events()
    return cast(Page, paginate(result))


@router.get(
    '/by_module',
    response_model=Page[schemas.Event],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_events_by_module(
    crud: EventCrud = Depends(EventCrud),
) -> Page[schemas.Event]:
    """Some description"""
    result: List = crud.get_all_events_by_module()
    return cast(Page, paginate(result))


@router.get(
    '/last',
    response_model=Page[schemas.Event],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_last_events(
    limit: int = 25,
    crud: EventCrud = Depends(EventCrud),
) -> Page[schemas.Event]:
    """Some description"""
    result: List = crud.get_last_events(limit)
    return cast(Page, paginate(result))


@router.post(                              # trying out new_add_event function
    '/add_event',
    # response_model=schemas.Event,
    status_code=status.HTTP_200_OK,

)
async def add_event(
    object_id: str,
    event: str,
    information: str,
    user_info: Dict = Depends(get_current_user),
    crud: EventCrud = Depends(EventCrud),
) -> None:
    """Some description"""
    try:
        LOG.info('API handling request to create a new virtual machine.')
        await run_in_threadpool(
            crud.new_add_event,
            object_id,
            user_info.get('id', ''),
            event,
            information,
        )
        LOG.info('API request was successfully processed.')
    except Exception as err:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        )


@router.get(
    '/download',
    response_model=schemas.DownloadResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def download_events(
    crud: EventCrud = Depends(EventCrud),
) -> StreamingResponse:
    """Download all events as a CSV file.

    This endpoint retrieves all events using the EventCrud class, generates
    a CSV file containing the event data, and returns it as a streaming
    response.

    Args:
        crud (EventCrud): Instance of EventCrud for database operations.

    Returns:
        StreamingResponse: A streaming response with the CSV file content.
    """
    result: List = crud.get_all_events()
    events_page: Page = paginate(
        result, params=Params(page=1, size=len(result))
    )

    # Создаем CSV файл в памяти
    output = io.StringIO()
    writer = csv.writer(output)

    # Записываем заголовки
    writer.writerow(
        [
            'id',
            'module',
            'object_id',
            'user_id',
            'event',
            'timestamp',
            'information',
        ]
    )

    # Записываем данные
    for event in events_page.items:
        writer.writerow(
            [
                event['id'],
                event['module'],
                event['object_id'],
                event['user_id'],
                event['event'],
                event['timestamp'],
                event['information'],
            ]
        )

    output.seek(0)

    return StreamingResponse(
        output,
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=logs.csv'},
    )
