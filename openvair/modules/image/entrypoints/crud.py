# noqa: D100
from typing import Any, Dict, Optional

from fastapi_pagination import paginate
from fastapi_pagination.bases import AbstractPage

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import validate_objects
from openvair.modules.image.config import (
    PERMITTED_EXTENSIONS,
    API_SERVICE_LAYER_QUEUE_NAME,
)
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.image.entrypoints import schemas
from openvair.modules.image.service_layer import services
from openvair.modules.image.entrypoints.exceptions import (
    NotSupportedExtensionError,
)

LOG = get_logger(__name__)


class ImageCrud:  # noqa: D101
    def __init__(self):  # noqa: D107
        self.service_layer_rpc = Protocol(client=True)(
            API_SERVICE_LAYER_QUEUE_NAME
        )

    @staticmethod
    def _check_image_extension(image_name: str) -> None:
        if ext := image_name.split('.')[-1] not in PERMITTED_EXTENSIONS:
            message = (
                'Incorrect extension of uploading image, '
                f'{ext} is not supported.'
            )
            LOG.error(message)
            raise NotSupportedExtensionError(message)

    def get_image(self, image_id: str) -> Dict:  # noqa: D102
        LOG.info('Call service layer on get image.')
        result = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.get_image.__name__,
            data_for_method={'image_id': image_id},
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def get_all_images(self, storage_id: Optional[str]) -> AbstractPage[Any]:  # noqa: D102
        LOG.info('Call service layer on get all images.')
        result = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.get_all_images.__name__,
            data_for_method={'storage_id': storage_id},
        )
        LOG.debug('Response from service layer: %s.' % result)
        images = validate_objects(result, schemas.Image)
        return paginate(images)

    def upload_image(  # noqa: D102
        self,
        name: str,
        storage_id: str,
        description: str,
        user_info: Dict,
    ) -> Dict:
        LOG.info('Call service layer on upload image.')
        self._check_image_extension(image_name=name)
        result = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.upload_image.__name__,
            data_for_method={
                'name': name,
                'storage_id': storage_id,
                'description': description,
                'user_info': user_info,
            },
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def delete_image(  # noqa: D102
        self,
        image_id: str,
        user_info: Dict,
    ) -> Dict:
        LOG.info('Call service layer on delete image.')
        result = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.delete_image.__name__,
            data_for_method={'image_id': image_id, 'user_info': user_info},
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def attach_image(  # noqa: D102
        self,
        image_id: str,
        data: Dict,
        user_info: Dict,
    ) -> Dict:
        data.update({'image_id': image_id, 'user_info': user_info})
        LOG.info('Call service layer on attach image.')
        result = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.attach_image.__name__,
            data_for_method=data,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def detach_image(  # noqa: D102
        self,
        image_id: str,
        detach_info: Dict,
        user_info: Dict,
    ) -> Dict:
        LOG.info('Call service layer on attach image.')
        detach_info.update({'image_id': image_id, 'user_info': user_info})
        result = self.service_layer_rpc.call(
            services.ImageServiceLayerManager.detach_image.__name__,
            data_for_method=detach_info,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result
