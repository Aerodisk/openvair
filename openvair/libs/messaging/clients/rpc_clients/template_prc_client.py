from typing import Dict, List  # noqa: D100

from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.template import (
    TemplateServiceLayerProtocolInterface,
)


class TemplateServiceLayerRPCClient(TemplateServiceLayerProtocolInterface):  # noqa: D101
    def __init__(self) -> None:
        """Initialize the StorageServiceLayerClient.

        This method sets up the necessary components for the
        StorageServiceLayerClient, including the RabbitMQ RPC client for
        communicating with the Storage Service Layer.
        """
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.Template.SERVICE_LAYER
        )

    def get_all_templates(self) -> List[Dict]:  # noqa: D102
        result: List[Dict] = self.service_rpc_client.call(
            TemplateServiceLayerProtocolInterface.get_all_templates.__name__,
            data_for_method={},
        )
        return result

    def get_template(self, getting_data: Dict) -> Dict:  # noqa: D102
        result: Dict = self.service_rpc_client.call(
            TemplateServiceLayerProtocolInterface.get_template.__name__,
            data_for_method=getting_data,
        )
        return result

    def create_template(self, creating_data: Dict) -> Dict:  # noqa: D102
        result: Dict = self.service_rpc_client.call(
            TemplateServiceLayerProtocolInterface.create_template.__name__,
            data_for_method=creating_data,
        )
        return result

    def edit_template(self, updating_data: Dict) -> Dict:  # noqa: D102
        result: Dict = self.service_rpc_client.call(
            TemplateServiceLayerProtocolInterface.edit_template.__name__,
            data_for_method=updating_data,
        )
        return result

    def delete_template(self, deleting_data: Dict) -> Dict:  # noqa: D102
        result: Dict = self.service_rpc_client.call(
            TemplateServiceLayerProtocolInterface.delete_template.__name__,
            data_for_method=deleting_data,
        )
        return result
