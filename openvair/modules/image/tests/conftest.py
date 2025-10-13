# noqa: D100
import os
from typing import BinaryIO
from pathlib import Path
from collections.abc import Generator

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from openvair.libs.testing.utils import (
    generate_image_name,
    wait_for_field_value,
    wait_full_deleting_file,
    generate_test_entity_name,
)
from openvair.modules.image.tests.utils import (
    test_delete_from_tmp,
    upload_image_api_call,
)


@pytest.fixture(scope='function')
def name() -> Generator[str, None, None]:
    """Creates valid image name."""
    name = generate_image_name()
    yield name
    test_delete_from_tmp(name)


@pytest.fixture(scope='function')
def long_name() -> Generator[str, None, None]:
    """Creates valid image name."""
    long_name = f'long-name-{"a" * 9}-{generate_image_name()}'
    yield long_name
    test_delete_from_tmp(long_name)


@pytest.fixture(scope='function')
def image_file() -> Generator[BinaryIO, None, None]:
    """Loads an image file."""
    load_dotenv(dotenv_path='/opt/aero/openvair/openvair/libs/testing/.env.test')
    env_path = os.getenv('TEST_IMAGE_PATH')
    if env_path is None:
        message = "Environment variable TEST_IMAGE_PATH is not set"
        raise ValueError(message)

    test_image_path = Path(env_path)
    with test_image_path.open("rb") as image:
        yield image


@pytest.fixture(scope='function')
def wrong_format_file() -> Generator[BinaryIO, None, None]:
    """Creates a non .iso image file"""
    file_path = Path(f'/opt/aero/openvair/openvair/modules/image/tests/'
                 f'{generate_test_entity_name("image_file")}')
    file_path.touch()
    with file_path.open("rb") as file:
        yield file
    file_path.unlink()
    wait_full_deleting_file(file_path)


@pytest.fixture(scope="function")
def image(
    client: TestClient,
    storage: dict,
    name: str,
    image_file: BinaryIO
) -> Generator[dict, None, None]:
    """Creates a test image and deletes it after each test."""
    storage_id = storage['id']
    query = {
        'storage_id': storage_id,
        'name': name
    }
    response = upload_image_api_call (name, query, client, image_file)
    data = response.json()
    storage_path = ('/opt/aero/openvair/data/mnt/'
                    f'{storage["storage_type"]}-{storage_id}')
    wait_for_field_value(
        client,
        f'/images/{data["id"]}/',
        'path',
        storage_path
    )
    response = client.get(f'/images/{data["id"]}')
    image = response.json()
    yield image
    client.delete(f"/images/{image['id']}")
