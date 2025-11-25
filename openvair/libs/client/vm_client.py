# noqa: D100
# in current moment this module is unused. It need to be adopted with actual rpc
# client functionality
from openvair.libs.client.base_client import BaseClient


# Unuse in current version need to be implemented from service interfaces and
# make polymorphic use for all clients
class VMClient(BaseClient):  # noqa: D101
    def __init__(self, access_token: str):  # noqa: D107
        super().__init__(service='virtual-machines', access_token=access_token)

    def get_vm(self, vm_id):  # noqa: ANN201, D102, ANN001
        vm_get_url = f'{self.url}/{vm_id}/'
        result = self.session.get(vm_get_url, headers=self.header)
        return result.json()
