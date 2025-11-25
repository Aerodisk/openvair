"""Creating RabbitMQ connection and managing requests."""

import json
from typing import TYPE_CHECKING, Any

import pika
from pika.adapters.blocking_connection import BlockingChannel

from openvair.modules.scheduler.config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.scheduler.service_layer.services import SchedulerService
from openvair.modules.scheduler.service_layer.exceptions import (
    MessageDoesNotHaveAction,
    BaseSchedulerServiceLayerException,
)
from openvair.modules.scheduler.service_layer.unit_of_work import (
    SchedulerSqlAlchemyUnitOfWork,
)

if TYPE_CHECKING:
    from pika.spec import Basic, BasicProperties


class SchedulerServiceManager:
    """Service layer's RPC-manager for API requests."""

    def __init__(self) -> None:
        """Initializing connection using config file."""
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )

        self.connection = pika.BlockingConnection(params)
        self.channel: BlockingChannel = self.connection.channel()

        self.channel.queue_declare(queue=API_SERVICE_LAYER_QUEUE_NAME)
        self.channel.queue_declare(queue=SERVICE_LAYER_DOMAIN_QUEUE_NAME)

        self.service = SchedulerService(SchedulerSqlAlchemyUnitOfWork)

    def _validate_action(self, action: str) -> None:
        """Validate that action is present."""
        if not action:
            msg = "Missing 'action' field in message"
            raise MessageDoesNotHaveAction(msg)

    def on_request(  # noqa: C901
        self,
        ch: BlockingChannel,
        method: 'Basic.Deliver',
        _properties: 'BasicProperties',
        body: bytes,
    ) -> None:
        """Handle incoming RPC request."""
        result: dict[str, Any] | list[dict[str, Any]]
        try:
            request = (
                json.loads(body.decode())
                if isinstance(body, bytes)
                else json.loads(body)
            )
            action = request.get('action')
            data = request.get('data', {})

            self._validate_action(action)

            if action == 'get_all':
                result = self.service.get_all_jobs()
            elif action == 'create':
                result = self.service.create_job(data)
            elif action == 'edit':
                result = self.service.edit_job(data.get('id'), data)
            elif action == 'delete':
                result = self.service.delete_job(data.get('id'))
            else:
                result = {'error': f'Unknown action: {action}'}

        except BaseSchedulerServiceLayerException as e:
            result = {'error': str(e)}

        ch.basic_publish(
            exchange='',
            routing_key=SERVICE_LAYER_DOMAIN_QUEUE_NAME,
            body=json.dumps(result).encode(),
        )
        delivery_tag = method.delivery_tag
        if delivery_tag is None:
            message = 'Missing delivery_tag on method'
            raise ValueError(message)

        ch.basic_ack(delivery_tag=delivery_tag)

    def start(self) -> None:
        """Start listening to RPC requests."""
        self.channel.basic_consume(
            queue=API_SERVICE_LAYER_QUEUE_NAME,
            on_message_callback=self.on_request,
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            pass
        finally:
            self.connection.close()
