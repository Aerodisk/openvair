"""RPC client and server implementation module.

This module provides classes for implementing an RPC client and server
using RabbitMQ as the transport layer.

Usage example:
    1.
        rpc_client = RabbitRPCClient('queue_name_1')
        # issubclass(data_for_manager, dict) == True
        result = rpc_client.call('manager_method_name', data_for_method)

        # Manager is a class that implements business logic or domain logic
        rpc_server = rpc.RPCServer('queue_name_1', Manager)

    2.
        self.rpc_client = rpc.RabbitRPCClient('queue_name_2')
        # issubclass(data_for_manager, dict) == True
        # data_for_manager is a parameter that will be passed to the manager
        # for its initialization. Additionally, method data can be passed here.
        result = self.rpc_client.call('method_name', data_for_manager=data)

        rpc_server = rpc.RabbitRPCServer('queue_name_2', manager)

Classes:
    RabbitRPCClient: Concrete implementation for rabbit rpc client.
    RabbitRPCServer: Concrete implementation for rabbit rpc server.
"""

import uuid
from typing import (
    Any,
    TypeVar,
    cast,
)
from collections.abc import Callable

import pika
from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel

from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
    RpcDeserializeMessageException,
)
from openvair.libs.messaging.rpc.rabbit_base import (
    BaseRabbitRPCClient,
    BaseRabbitRPCServer,
)
from openvair.libs.data_handlers.json.serializer import (
    serialize_json,
    deserialize_json,
)

T = TypeVar('T')


class RabbitRPCClient(BaseRabbitRPCClient):
    """Concrete implementation for rabbit rpc client.

    This class sends messages to the RPC server and processes responses.

    Attributes:
        queue_name (str): Name of the queue to send messages to.
    """

    def __init__(self, queue_name: str, callback_queue_name: str = ''):
        """Initialize the RPC client with a specific queue.

        Args:
            queue_name (str): The name of the queue to send messages to.
            callback_queue_name (str): The name of the callback queue.
                Defaults to an empty string, which triggers automatic
                generation of a unique queue name.
        """
        super().__init__(queue_name, callback_queue_name)
        self.corr_id: str | None

    def on_response(
        self,
        channel: BlockingChannel,  # noqa: ARG002 need for rabbitmq basic_consume
        method: Basic.Deliver,  # noqa: ARG002 need for rabbitmq basic_consume
        props: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Process incoming responses from the RPC server.

        This method deserializes the message body and stores the result in
        the `self.response` attribute.

        Args:
            channel: The channel on which the message was received.
            method: Delivery method.
            props: Message properties.
            body: The body of the message.
        """
        if self.corr_id == props.correlation_id:
            try:
                self.response = deserialize_json(body.decode('utf-8'))
            except ValueError as err:
                raise RpcDeserializeMessageException(str(err))

    def call(
        self,
        method_name: str,
        data_for_method: dict | None = None,
        data_for_manager: dict | None = None,
        *,
        priority: int = 1,
        time_limit: int = 100,
    ) -> Any:  # noqa: ANN401 TODO need to spicify response by pydantic
        """Send a request to the RPC server and wait for a response.

        Args:
            method_name (str): The name of the method to be called on the
                server.
            data_for_method (Optional[Dict]): The data to be passed to the
                method.
            data_for_manager (Optional[Dict]): The data for initializing the
                manager.
            priority (int): The priority of the message. Defaults to 1.
            time_limit (int): The time limit for waiting for a response.
                Defaults to 100.

        Returns:
            Dict: The result of the method call on the RPC server.

        Raises:
            RpcCallTimeoutException: If the response is not received within the
                time limit.
            RpcCallException: If the RPC server returns an error.
        """
        self.response = {}
        self.corr_id = str(uuid.uuid4())
        try:
            serialized_data = serialize_json(
                {
                    'method_name': method_name,
                    'data_for_method': data_for_method,
                    'data_for_manager': data_for_manager,
                }
            ).encode()
        except TypeError as err:
            msg = f'Error serializing RPC request: {err}'
            raise RpcCallException(msg)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                priority=priority,
            ),
            body=serialized_data,
        )
        # Wait for a response from the RPC server
        self.connection.process_data_events(time_limit=time_limit)
        if not self.response:
            message = (
                f'connection timeout expired: '
                f'{self.params.blocked_connection_timeout}'
            )
            raise RpcCallTimeoutException(message)
        if self.response.get('err'):
            raise RpcCallException(str(self.response['err']))
        return self.response.get('data', {})

    def cast(
        self,
        method_name: str,
        data_for_method: dict | None = None,
        data_for_manager: dict | None = None,
        *,
        priority: int = 10,
    ) -> None:
        """Send a request to the RPC server without waiting for a response.

        Args:
            method_name (str): The name of the method to be called on the
                server.
            data_for_method (Optional[Dict]): The data to be passed to the
                method.
            data_for_manager (Optional[Dict]): The data for initializing the
                manager.
            priority (int): The priority of the message. Defaults to 10.
        """
        self.corr_id = str(uuid.uuid4())
        try:
            serialized_data = serialize_json(
                {
                    'method_name': method_name,
                    'data_for_method': data_for_method,
                    'data_for_manager': data_for_manager,
                }
            ).encode()
        except TypeError as err:
            msg = f'Error serializing RPC request: {err}'
            raise RpcCallException(msg)

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                correlation_id=self.corr_id, priority=priority
            ),
            body=serialized_data,
        )


class RabbitRPCServer(BaseRabbitRPCServer):
    """Concrete implementation for rabbit rpc server.

    This class listens for incoming messages, initializes a manager, and
    executes the appropriate method on the manager.

    Attributes:
        manager: The manager class whose methods will be executed.
    """

    def __init__(self, queue_name: str, manager: Callable):
        """Initialize the RPC server and start listening to the queue.

        Args:
            queue_name (str): The name of the queue to listen to.
            manager (Type): The manager class whose methods will be executed.
        """
        super().__init__(queue_name, manager)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.on_request
        )

    def start(self) -> None:
        """Starts server instance"""
        self.channel.start_consuming()

    def on_request(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        props: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Process incoming requests from the RPC client.

        This method deserializes the message, initializes the manager,
        and executes the appropriate method. The result is sent back
        to the client.

        Args:
            channel: The channel on which the message was received.
            method: Delivery method.
            props: Message properties.
            body: The body of the message.
        """
        try:
            deserialized_body = deserialize_json(body.decode('utf-8'))
        except ValueError as err:
            msg = f'Error deserializing RPC message: {err}'
            raise RpcDeserializeMessageException(msg)
        method_name = deserialized_body.get('method_name', None)
        data_for_method = deserialized_body.get('data_for_method', {})
        data_for_manager = deserialized_body.get('data_for_manager', {})
        request = {}
        try:
            inited_manager = (
                self.manager(data_for_manager)
                if data_for_manager
                else self.manager()
            )
            managers_method = getattr(inited_manager, method_name)
            result = (
                managers_method(data_for_method)
                if data_for_method
                else managers_method()
            )
            request.update({'data': result})
        except Exception as err:  # noqa: BLE001 because it's catching all exceptions
            request.update({'err': str(err)})
        try:
            serialized_request = serialize_json(request)
        except TypeError as err:
            serialized_request = serialize_json({'err': str(err)})
        if props.reply_to:
            channel.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=props.correlation_id
                ),
                body=serialized_request.encode(),
            )
        channel.basic_ack(delivery_tag=cast('int', method.delivery_tag))
