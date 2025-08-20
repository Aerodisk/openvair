"""Integration tests for creating templates via API.

Covers:
- Successful creation with both is_backing values.
- Missing required fields.
- Unauthorized access.
- Invalid storage/base_volume_id.
- Edge cases for null and nonexistent base_volume_id.
"""

from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.testing.config import image_settings
from openvair.modules.image.tests.conftest import (
    generate_image_name,
    generate_random_string,
)

# тесты для upload_image

image_path = image_settings.image_path


def test_upload_image_success(
    client: TestClient,
    storage: Dict,
) -> None:
    """Some description"""
    storage_id = storage['id']
    name = generate_image_name()
    with open(image_path, "rb") as file:  # noqa: PTH123
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    assert response.status_code == status.HTTP_200_OK


def test_upload_image_success_with_description(
    client: TestClient,
    storage: Dict,
) -> None:
    """Some description"""
    storage_id = storage['id']
    description = generate_random_string(10)
    name = generate_image_name()
    with open(image_path, "rb") as file:  # noqa: PTH123
        response = client.post(
            f"/images/upload/?storage_id={storage_id}&description={description}&name={name}",
            files={"image": (name, file, "application/x-cd-image")},
        )
    assert response.status_code == status.HTTP_200_OK


# неавторизованный 401
# нет обязательных полей (имя, сторадж, образ)
# неправильный path либо файл не того формата
# невалидный сторадж id
# некорректные значения (слишком длинные, не тот формат имени)
# некорректные типы данных
# проверять удаление файла в tmp
