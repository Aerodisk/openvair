"""Messaging utilities module.

This module provides utility functions for serializing and deserializing
messages between the RPC client and server.

Functions:
    serialize: Converts a dictionary to a JSON string for transmission.
    deserialize: Converts a JSON string to a dictionary after receiving a
        message.
"""

import json
from typing import Dict

from openvair.libs.messaging.exceptions import RpcDeserializeMessageException


def serialize(data: Dict) -> str:
    """Convert a dictionary to a JSON string.

    This function serializes a dictionary into a JSON string for sending
    as a message to the RPC server.

    Args:
        data (Dict): The dictionary to be serialized.

    Returns:
        str: The serialized JSON string.
    """
    return str(json.dumps(data, skipkeys=True))


def deserialize(message: bytes) -> Dict:
    """Convert a JSON string to a dictionary.

    This function deserializes a JSON string received from the RPC server
    back into a dictionary.

    Args:
        message (bytes): The JSON string received from the RPC server.

    Returns:
        Dict: The deserialized dictionary.
    """
    try:
        deserialized_message: Dict = json.loads(message.decode('utf-8'))
    except (json.JSONDecodeError, TypeError) as err:
        raise RpcDeserializeMessageException(str(err))
    else:
        return deserialized_message
