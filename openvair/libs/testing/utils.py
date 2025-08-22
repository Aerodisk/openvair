"""Testing utilities for OpenVair integration tests.

This module provides common utility functions for creating, deleting,
and managing test resources during integration testing. It includes
functions for:

- Creating resources via API endpoints
- Deleting resources via API endpoints
- Generating unique test entity names
- Cleaning up test volumes
"""

import time
import uuid
import string
import secrets
from typing import Any, Dict, cast

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.domain.model import VolumeFactory
from openvair.modules.volume.adapters.serializer import (
    DataSerializer as VolumeSerializer,
)
from openvair.modules.image.service_layer.unit_of_work import (
    ImageSqlAlchemyUnitOfWork,
)
from openvair.modules.volume.service_layer.unit_of_work import (
    VolumeSqlAlchemyUnitOfWork as VolumeUOW,
)
from openvair.modules.template.service_layer.unit_of_work import (
    TemplateSqlAlchemyUnitOfWork,
)

LOG = get_logger(__name__)


def create_resource(
    client: TestClient, endpoint: str, payload: dict, resource_name: str
) -> Dict[str, Any]:
    """Creates a resource on a specified endpoint using the provided client and payload.

    This function sends a POST request to create a resource at the specified endpoint using the
    given client and payload. It validates the HTTP status code of the response and raises an
    exception if the resource creation is unsuccessful. If successful, it returns the response
    data as a dictionary.

    Args:
        client: The test client instance used to send the POST request.
        endpoint: The endpoint URL where the resource should be created.
        payload: The payload data to be sent in the POST request.
        resource_name: The name of the resource being created, used in error messages.

    Returns:
        A dictionary containing the response data from the successful resource creation.

    Raises:
        RuntimeError: If the response status code is not one of the permissible codes
        (200, 201, 202).
    """  # noqa: E501, W505
    response = client.post(endpoint, json=payload)
    if response.status_code not in (
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
        status.HTTP_202_ACCEPTED,
    ):
        msg = (
            f'Failed to create {resource_name}: '
            f'{response.status_code}, '
            f'{response.text}'
        )
        raise RuntimeError(msg)
    return cast(Dict[str, Any], response.json())


def delete_resource(
    client: TestClient, endpoint: str, resource_id: str, resource_name: str
) -> None:
    """Deletes a resource from the specified endpoint using the provided client.

    This function sends a delete request to the given endpoint to delete the
    specified resource. If the deletion is unsuccessful, it logs a warning
    message indicating the failure, including the status code and response text.

    Args:
        client: Instance of the TestClient used to send the delete request.
        endpoint: API endpoint where the resource is located.
        resource_id: Unique identifier of the resource to be deleted.
        resource_name: Human-readable name of the resource being deleted, used
            for logging purposes.

    """
    response = client.delete(f'{endpoint}/{resource_id}/')
    if response.status_code not in (
        status.HTTP_202_ACCEPTED,
        status.HTTP_200_OK,
    ):
        LOG.warning(
            f'{resource_name.capitalize()} deletion failed: '
            f'{response.status_code}, '
            f'{response.text}'
        )


def generate_test_entity_name(entity_type: str, prefix: str = 'test') -> str:
    """Generate a unique name for a test entity.

    Creates a name in the format "{prefix}-{entity_type}-{uuid}" where uuid
    is a 6-character random hex string. This ensures unique names for test
    entities while maintaining readability.

    Args:
        entity_type: The type of entity (e.g. 'volume', 'storage')
        prefix: Optional prefix to prepend to the name (default: 'test')

    Returns:
        A unique name string for the test entity
    """
    return f'{prefix}-{entity_type}-{uuid.uuid4().hex[:6]}'


def generate_random_string(length: int) -> str:
    """Generates a random string with a certain length."""
    letters = string.ascii_lowercase
    return ''.join(secrets.choice(letters) for _ in range(length))


def generate_image_name() -> str:
    """Generates a unique name for an image."""
    return f'{generate_test_entity_name("image")}.iso'


def cleanup_all_volumes() -> None:
    """Remove all volumes from both database and filesystem.

    This utility function is typically used after storage tests to ensure
    a clean state. It:
    1. Retrieves all volumes from the database
    2. For each volume:
        - Creates a domain model instance
        - Deletes the volume record from the database
        - Removes the volume file from the filesystem
        - Commits the transaction

    Any errors during cleanup are logged as warnings but do not interrupt
    the cleanup process.
    """
    unit_of_work = VolumeUOW()
    try:
        with unit_of_work as uow:
            volumes = uow.volumes.get_all()
            for orm_volume in volumes:
                volume_instance = VolumeFactory().get_volume(
                    VolumeSerializer.to_domain(orm_volume)
                )
                uow.volumes.delete(orm_volume)
                volume_instance.delete()
            uow.commit()
    except Exception as err:  # noqa: BLE001
        LOG.warning(f'Error while cleaning up volumes: {err}')


def cleanup_all_templates() -> None:
    """Remove all volumes from both database and filesystem.

    This utility function is typically used after storage tests to ensure
    a clean state. It:
    1. Retrieves all volumes from the database
    2. For each volume:
        - Creates a domain model instance
        - Deletes the volume record from the database
        - Removes the volume file from the filesystem
        - Commits the transaction

    Any errors during cleanup are logged as warnings but do not interrupt
    the cleanup process.
    """
    unit_of_work = TemplateSqlAlchemyUnitOfWork()
    try:
        with unit_of_work as uow:
            templates = uow.templates.get_all()
            for orm_template in templates:
                uow.templates.delete(orm_template)
                uow.commit()
    except Exception as err:  # noqa: BLE001
        LOG.warning(f'Error while cleaning up volumes: {err}')


def cleanup_all_images() -> None:
    """Remove all volumes from both database and filesystem.

    This utility function is typically used after storage tests to ensure
    a clean state. It:
    1. Retrieves all volumes from the database
    2. For each volume:
        - Creates a domain model instance
        - Deletes the volume record from the database
        - Removes the volume file from the filesystem
        - Commits the transaction

    Any errors during cleanup are logged as warnings but do not interrupt
    the cleanup process.
    """
    unit_of_work = ImageSqlAlchemyUnitOfWork()
    try:
        with unit_of_work as uow:
            images = uow.images.get_all()
            for orm_image in images:
                uow.images.delete(orm_image)
                uow.commit()
    except Exception as err:  # noqa: BLE001
        LOG.warning(f'Error while cleaning up volumes: {err}')


def wait_for_field_value(  # noqa: PLR0913
    client: TestClient,
    path: str,
    field: str,
    expected: Any,  # noqa: ANN401
    timeout: int = 30,
    interval: float = 0.5,
) -> None:
    """Polls a GET endpoint until a specific field reaches expected value.

    Compatible with both plain and BaseResponse-style APIs.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get(path)
        if response.status_code == status.HTTP_200_OK:
            raw = response.json()
            data = (
                raw['data']
                if 'data' in raw and isinstance(raw['data'], dict)
                else raw
            )
            if data.get(field) == expected:
                return
        time.sleep(interval)
    message = (
        f'Field "{field}" at "{path}" did not become "{expected}" '
        f'within {timeout} seconds.'
    )
    raise TimeoutError(message)


def wait_until_404(
    client: TestClient,
    template_id: str,
    timeout: int = 30,
    interval: float = 0.5,
) -> None:
    """Wait until GET /templates/{id} returns 500, indicating deletion.

    Args:
        client (TestClient): The test client to use.
        template_id (str): ID of the template to wait for disappearance.
        timeout (int): Maximum wait time in seconds.
        interval (float): Interval between retries.

    Raises:
        TimeoutError: If template is still available after timeout.
    """
    url = f'/templates/{template_id}'
    start = time.time()
    while time.time() - start < timeout:
        response = client.get(url)
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return
        time.sleep(interval)
    message = f'Template {template_id} not deleted within {timeout} seconds'
    raise TimeoutError(message)


def wait_full_deleting(
    client: TestClient,
    path: str,
    object_id: str,
    timeout: int = 30,
    interval: float = 0.5,
) -> None:
    """Polls a GET endpoint until a specific object is fully deleted.

    This function repeatedly sends GET requests to a given path and checks
    whether the object with the specified ID is absent in the response.
    It is useful for ensuring that deletion has fully propagated.

    Args:
        client (TestClient): The test client to use for sending requests.
        path (str): The API path to poll for object presence.
        object_id (str): The ID of the object to wait for deletion.
        timeout (int): Maximum wait time in seconds before timing out.
        interval (float): Time in seconds between successive requests.

    Raises:
        TimeoutError: If the object is still present after the timeout expires.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get(path)
        if response.status_code == status.HTTP_200_OK:
            raw = response.json()
            data = (
                raw['data']
                if 'data' in raw and isinstance(raw['data'], dict)
                else raw
            )
            if data.get(object_id) is None:
                return
            time.sleep(interval)
    message = (
        f'Object with id "{object_id}" at "{path}" was not deleted '
        f'within {timeout} seconds.'
    )
    raise TimeoutError(message)


def _extract_data_field(response_json: Dict) -> Dict:
    """Returns response['data'] if it's a BaseResponse, else root object."""
    if 'data' in response_json and isinstance(response_json['data'], dict):
        return response_json['data']
    return response_json
