from typing import Dict, BinaryIO  # noqa: D100
from pathlib import Path

from httpx import Response
from fastapi.testclient import TestClient

from openvair.config import TMP_DIR
from openvair.libs.testing.utils import wait_full_deleting_file


def test_delete_from_tmp (name: str) -> None:
    """Function tests if a file was deleted from tmp within timeout seconds"""
    file_path = Path(TMP_DIR, name)
    timeout = 30
    try:
        wait_full_deleting_file(file_path, timeout=timeout)
    except TimeoutError:
        file_path.unlink()
        message = f'"{file_path}" was not deleted within {timeout} seconds.'
        raise TimeoutError(message)

def upload_image_api_call (
        name: str,
        query: Dict,
        client: TestClient,
        image: BinaryIO
    ) -> Response:
    """A function which uploads an image and returns a Response"""
    api = '/images/upload/?'
    for key, value in query.items():
        api += f'{key}={value}&'
    api = api[:-1]
    return client.post(
        api,
        files={"image": (name, image, "application/x-cd-image")},
    )
