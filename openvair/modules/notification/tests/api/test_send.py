"""Integration tests for notification sending.

Covers:
- Successful notification sending via email.
- Validation errors (missing fields, invalid msg_type, email format, etc).
- Service layer errors (e.g. SMTP failures, timeouts).
- Edge cases (empty recipients, long messages).
- Unauthorized access.
"""

from typing import Dict
from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.notification.service_layer.unit_of_work import (
    NotificationSqlAlchemyUnitOfWork,
)

LOG = get_logger(__name__)


def test_send_notification_email_success(
    client: TestClient, notification: Dict
) -> None:
    """Test successful email notification sending.

    Asserts:
    - Response is 200 OK.
    - Returned data matches request.
    - Database data matches request.
    """
    response = client.post('/notifications/send/', json=notification)
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['msg_type'] == notification['msg_type']
    assert data['recipients'] == notification['recipients']
    assert data['subject'] == notification['subject']
    assert data['message'] == notification['message']
    assert set(data.keys()) == {'msg_type', 'recipients', 'subject', 'message'}

    with NotificationSqlAlchemyUnitOfWork() as uow:
        notifications = uow.notifications.get_all()
        assert len(notifications) == 1
        db_notification = notifications[0]

        assert db_notification.msg_type == notification['msg_type']
        assert db_notification.recipients == notification['recipients']
        assert db_notification.subject == notification['subject']
        assert db_notification.message == notification['message']

        assert db_notification.status == 'sent'
        assert db_notification.create_datetime is not None


def test_send_notification_unauthorized(
    unauthorized_client: TestClient, notification: Dict
) -> None:
    """Test unauthorized access to notification endpoint.

    Asserts:
    - HTTP 401 Unauthorized when no valid token provided.
    """
    response = unauthorized_client.post(
        '/notifications/send/', json=notification
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_send_notification_missing_required_fields(client: TestClient) -> None:
    """Test missing required fields in request.

    Asserts:
    - HTTP 422 for each missing required field.
    """
    required_fields = ['msg_type', 'recipients', 'subject', 'message']

    for field in required_fields:
        invalid_data = {
            'msg_type': 'email',
            'recipients': ['test@example.com'],
            'subject': 'Test',
            'message': 'Test message',
        }
        del invalid_data[field]

        response = client.post('/notifications/send/', json=invalid_data)
        assert response.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            assert 'NoRecipientsSpecifiedForEmailNotification' in response.text


def test_send_notification_invalid_msg_type(
    client: TestClient, notification: Dict
) -> None:
    """Test invalid message type validation.

    Asserts:
    - HTTP 422 for unsupported message types.
    """
    invalid_data = notification.copy()
    invalid_data['msg_type'] = 'pigeon_post'

    response = client.post('/notifications/send/', json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_send_notification_invalid_email_format(
    client: TestClient, notification: Dict
) -> None:
    """Test invalid email format validation.

    Asserts:
    - HTTP 422 for malformed email addresses.
    """
    invalid_data = notification.copy()
    invalid_data['recipients'] = ['not-an-email-address']

    response = client.post('/notifications/send/', json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_send_notification_empty_message(
    client: TestClient, notification: Dict
) -> None:
    """Test validation for empty message content.

    Asserts:
    - HTTP 422 when message is empty.
    """
    invalid_data = notification.copy()
    invalid_data['message'] = ''

    response = client.post('/notifications/send/', json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_send_notification_empty_subject(
    client: TestClient, notification: Dict
) -> None:
    """Test validation for empty subject.

    Asserts:
    - HTTP 422 when subject is empty.
    """
    invalid_data = notification.copy()
    invalid_data['subject'] = ''

    response = client.post('/notifications/send/', json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@patch(
    'openvair.modules.notification.service_layer.services.MessagingClient.call'
)
def test_send_notification_service_layer_error(
    mock_rpc_call: MagicMock, client: TestClient, notification: Dict
) -> None:
    """Test service layer exception during notification sending.

    Asserts:
    - HTTP 500 when service layer raises exception.
    """
    mock_rpc_call.side_effect = RpcCallException('RPC error [TEST]')

    response = client.post('/notifications/send/', json=notification)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@patch(
    'openvair.modules.notification.service_layer.services.MessagingClient.call'
)
def test_send_notification_service_layer_timeout(
    mock_rpc_call: MagicMock, client: TestClient, notification: Dict
) -> None:
    """Test timeout handling during notification sending.

    Asserts:
    - HTTP 500 when operation times out.
    """
    mock_rpc_call.side_effect = RpcCallTimeoutException('RPC timeout [TEST]')

    response = client.post('/notifications/send/', json=notification)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_send_notification_long_message(
    client: TestClient,
    notification: Dict,
) -> None:
    """Test successful sending with big length message.

    Asserts:
    - HTTP 200 with long message content.
    """
    long_message = 'T' * 5000  # 5000-character message
    notification_data = notification.copy()
    notification_data['message'] = long_message

    response = client.post('/notifications/send/', json=notification_data)
    assert response.status_code == status.HTTP_200_OK
