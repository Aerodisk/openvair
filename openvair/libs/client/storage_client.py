# noqa: D100
# in current moment this module is unused. It need to be adopted with actual rpc
# client functionality
from typing import Optional

from openvair.libs.client.base_client import BaseClient


# Unuse in current version need to be implemented from service interfaces and
# make polymorphic use for all clients
class StorageClient(BaseClient):  # noqa: D101
    def __init__(self, access_token: Optional[str] = None):  # noqa: D107
        super().__init__(service='storages', access_token=access_token)

    def get_storage_by_id(self, storage_id):  # noqa: D102, ANN201, ANN001
        storage_url = f'{self.url}/{storage_id}/'
        result = self.session.get(storage_url, headers=self.header)
        return result.json()

    def get_all_storages(self):  # noqa: D102, ANN201
        storage_url = f'{self.url}/'
        result = self.session.get(storage_url, headers=self.header)
        return result.json().get('items', [])
