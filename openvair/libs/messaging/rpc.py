"""RPC client and server implementation module.

This module provides classes for implementing an RPC client and server
using RabbitMQ as the transport layer. The RPC implementation is based
on the Builder pattern.

Usage example:
    1.
        rpc_client = RPCClient('queue_name_1')
        # issubclass(data_for_manager, dict) == True
        result = rpc_client.call('manager_method_name', data_for_method)

        # Manager is a class that implements business logic or domain logic
        rpc_server = rpc.RPCServer('queue_name_1', Manager)

    2.
        self.rpc_client = rpc.RPCClient('queue_name_2')
        # issubclass(data_for_manager, dict) == True
        # data_for_manager is a parameter that will be passed to the manager
        # for its initialization. Additionally, method data can be passed here.
        result = self.rpc_client.call('method_name', data_for_manager=data)

        rpc_server = rpc.RPCServer('queue_name_2', manager)

Classes:
    BaseRabbitRPCClient: Base class for implementing an RPC client.
    RabbitRPCClient: Class for implementing an RPC client with RabbitMQ.
    BaseRabbitRPCServer: Base class for implementing an RPC server.
    RabbitRPCServer: Class for implementing an RPC server with RabbitMQ.
"""

import uuid
from abc import abstractmethod
from typing import Dict, Type, Optional

import pika
from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel

from openvair.libs.messaging import utils
from openvair.libs.messaging.transport import rabbitmq
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)


class BaseRabbitRPCClient(rabbitmq.BaseRabbitMQConnection):
    """Base implementation of an RPC client.

    This class creates a callback queue for receiving responses from the
    RPC server.

    Attributes:
        callback_queue_name (str): Name of the callback queue.
        callback_queue (str): The declared callback queue.
        response (dict): Stores the server response.
        corr_id (str): Correlation ID for matching responses.
    """

    def __init__(self, callback_queue_name: str = ''):
        """Initialize the RPC client with a callback queue.

        Args:
            callback_queue_name (str): The name of the callback queue.
                Defaults to an empty string, which triggers automatic
                generation of a unique queue name.
        """
        self.callback_queue_name = callback_queue_name
        super().__init__()
        result = self.channel.queue_declare(
            queue=self.callback_queue_name,
            exclusive=True,
            arguments={'x-max-priority': 10, 'x-max-length': 200},
        )
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.response = {}
        self.corr_id = None

    @abstractmethod
    def on_response(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        props: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Handle incoming responses from the RPC server.

        This method is intended to be overridden by subclasses.

        Args:
            channel: The channel on which the message was received.
            method: Delivery method.
            props: Message properties.
            body: The body of the message.
        """
        raise NotImplementedError


class RabbitRPCClient(BaseRabbitRPCClient):
    """Implementation of an RPC client using RabbitMQ.

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
        super().__init__(callback_queue_name)
        self.queue_name = queue_name

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
            self.response = utils.deserialize(body)

    def call(
        self,
        method_name: str,
        data_for_method: Optional[Dict] = None,
        data_for_manager: Optional[Dict] = None,
        priority: int = 1,
        time_limit: int = 100,
    ) -> Dict:
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
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                priority=priority,
            ),
            body=utils.serialize(
                {
                    'method_name': method_name,
                    'data_for_method': data_for_method,
                    'data_for_manager': data_for_manager,
                }
            ),
        )
        # Wait for a response from the RPC server
        self.connection.process_data_events(time_limit=time_limit)
        if not self.response:
            raise RpcCallTimeoutException
        if self.response.get('err', None):
            raise RpcCallException(str(self.response['err']))
        return self.response.get('data', {})

    def cast(
        self,
        method_name: str,
        data_for_method: Optional[Dict] = None,
        data_for_manager: Optional[Dict] = None,
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
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                correlation_id=self.corr_id, priority=priority
            ),
            body=utils.serialize(
                {
                    'method_name': method_name,
                    'data_for_method': data_for_method,
                    'data_for_manager': data_for_manager,
                }
            ),
        )


class BaseRabbitRPCServer(rabbitmq.BaseRabbitMQConnection):
    """Base implementation of an RPC server.

    This class declares the queue for listening to incoming messages.
    """

    def __init__(self, queue_name: str):
        """Initialize the RPC server with a specific queue.

        Args:
            queue_name (str): The name of the queue to listen to.
        """
        super().__init__()
        self.channel.queue_declare(
            queue=queue_name,
            arguments={'x-max-priority': 10, 'x-max-length': 200},
        )


class RabbitRPCServer(BaseRabbitRPCServer):
    """Implementation of an RPC server using RabbitMQ.

    This class listens for incoming messages, initializes a manager, and
    executes the appropriate method on the manager.

    Attributes:
        manager: The manager class whose methods will be executed.
    """

    def __init__(self, queue_name: str, manager: Type):
        """Initialize the RPC server and start listening to the queue.

        Args:
            queue_name (str): The name of the queue to listen to.
            manager: The manager class whose methods will be executed.
        """
        self.manager = manager
        super().__init__(queue_name)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.on_request
        )
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
        deserialized_body = utils.deserialize(body)
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
            serialized_request = utils.serialize(request)
        except TypeError as err:
            serialized_request = utils.serialize({'err': str(err)})
        if props.reply_to:
            channel.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=props.correlation_id
                ),
                body=serialized_request,
            )
        channel.basic_ack(delivery_tag=method.delivery_tag)
