# noqa: D100
# in current moment this module is unused. It need to be adopted with actual rpc
# client functionality
from openvair.libs.client.base_client import BaseClient


# Unuse in current version need to be implemented from service interfaces and
# make polymorphic use for all clients
class ImageClient(BaseClient):  # noqa: D101
    def __init__(self, access_token: str):  # noqa: D107
        super().__init__(
            service='images', access_token=access_token
        )

    def attach_image(self, image_id: str, attach_info: dict):  # noqa: D102, ANN201
        image_attach_url = f'{self.url}/{image_id}/attach/'
        result = self.session.post(
            image_attach_url, json=attach_info, headers=self.header
        )
        return result.json()

    def get_images_by_storage_id(self, storage_id: str):  # noqa: ANN201, D102
        image_get_url = f'{self.url}/'
        result = self.session.get(
            image_get_url,
            params={'storage_id': storage_id},
            headers=self.header,
        )
        return result.json().get('items', [])

    def detach_image(self, image_id: str, detach_info: dict):  # noqa: D102, ANN201
        image_detach_url = f'{self.url}/{image_id}/detach/'
        result = self.session.delete(
            image_detach_url, json=detach_info, headers=self.header
        )
        return result.json()
