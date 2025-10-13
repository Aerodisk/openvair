"""API endpoints for notification management.

This module defines the API routes for managing notifications, including
endpoints for sending notifications through various channels like email and
SMS. It uses FastAPI to handle requests and responses, and integrates with the
NotificationCrud class to perform the necessary operations.

Endpoints:
    - POST /notifications/send/ - Send a notification to specified recipients.

Dependencies:
    - get_current_user: Dependency for retrieving the current authenticated
        user.
    - NotificationCrud: Class for handling CRUD operations related to
        notifications.
"""


from fastapi import Depends, APIRouter, status
from starlette.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import get_current_user
from openvair.modules.notification.entrypoints import schemas
from openvair.modules.notification.entrypoints.crud import NotificationCrud

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/notifications',
    tags=['notification'],
    responses={404: {'description': 'Not found!'}},
)


@router.post(
    '/send/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.Notification,
    dependencies=[Depends(get_current_user)],
)
async def send_notification(
    data: schemas.Notification,
    crud: NotificationCrud = Depends(NotificationCrud),
) -> schemas.Notification | JSONResponse:
    """Send a notification to the specified recipients.

    This endpoint sends a notification based on the provided data. The
    notification is processed and sent asynchronously.

    Args:
        data (schemas.Notification): Information about the notification to send.
        crud (NotificationCrud): Dependency injection for the NotificationCrud
            class.

    Returns:
        schemas.Notification: The notification object retrieved from the
            database.

    Raises:
        JSONResponse: If the notification sending fails, a 500 error response
            is returned with the error details.
    """
    LOG.info(
        f'API start sending notification with data: {data.model_dump()}.'
    )
    result = await run_in_threadpool(
        crud.send_notification, data.model_dump(mode='json')
    )

    if result.get('status') == 'error':
        LOG.error(result)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result
        )

    return schemas.Notification(**result)
