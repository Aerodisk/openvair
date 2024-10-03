# noqa: D100
# in current moment this module is unused. It need to be adopted with actual rpc
# client functionality
from openvair.libs.client.base_client import BaseClient


# Unuse in current version need to be implemented from service interfaces and
# make polymorphic use for all clients
class VolumeClient(BaseClient):  # noqa: D101
    def __init__(self, access_token: str):  # noqa: D107
        super().__init__(
            service='volumes', access_token=access_token
        )

    def get_volume(self, volume_id):  # noqa: D102, ANN201, ANN001
        volume_get_url = f'{self.url}/{volume_id}/'
        result = self.session.get(volume_get_url, headers=self.header)
        return result.json()

    def get_volumes_by_storage_id(self, storage_id: str):  # noqa: ANN201, D102
        volume_get_url = f'{self.url}/'
        result = self.session.get(
            volume_get_url,
            params={'storage_id': storage_id},
            headers=self.header,
        )
        return result.json().get('items', [])

    def create_volume(self, volume_info: dict):  # noqa: ANN201, D102
        volume_create_url = f'{self.url}/create/'
        result = self.session.post(
            volume_create_url, json=volume_info, headers=self.header
        )
        return result.json()

    def attach_volume(self, volume_id: str, attach_info: dict):  # noqa: ANN201, D102
        volume_attach_url = f'{self.url}/{volume_id}/attach/'
        result = self.session.post(
            volume_attach_url, json=attach_info, headers=self.header
        )
        return result.json()

    def detach_volume(self, volume_id: str, detach_info: dict):  # noqa: ANN201, D102
        volume_detach_url = f'{self.url}/{volume_id}/detach/'
        result = self.session.delete(
            volume_detach_url, json=detach_info, headers=self.header
        )
        return result.json()

    def delete_volume(self, volume_id: str):  # noqa: ANN201, D102
        volume_delete_url = f'{self.url}/{volume_id}/delete/'
        result = self.session.delete(volume_delete_url, headers=self.header)
        return result.json()
