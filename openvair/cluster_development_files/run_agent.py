import os  # noqa: D100

from openvair.libs.log import get_logger
from openvair.libs.messaging.messaging_agents import MessagingServer
from openvair.cluster_development_files.vm_manager_dryrun import VmManagerDryRun

NODE_NAME = os.environ['NODE_NAME']

LOG = get_logger(__name__)


def start_vm_server():  # type: ignore  # noqa: ANN201, D103
    LOG.info('Starting VM server')
    queue = f'vm.req.{NODE_NAME}'
    service = VmManagerDryRun
    service.start(block=False)
    server = MessagingServer(
        queue_name=queue,
        manager=service,
    )
    LOG.info('Starting VM server 2')
    server.start()


if __name__ == '__main__':
    start_vm_server()
