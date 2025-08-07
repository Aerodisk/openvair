from typing import Any  # noqa: D100

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.user.tests.api.conftest import FIXED_USER_ID


def test_create_user_authorized_admin(authorized_user_admin: Any) -> None:  # noqa: ANN401, D103
    client, user_id = authorized_user_admin

    user_data = {
        "username": "test_user_created",
        "email": "test_user_created@example.com",
        "is_superuser": True,
        "password": "string"
    }

    headers = {"Authorization": "Bearer fake-token"}

    response = client.post(f"/user/{user_id}/create/", json=user_data, headers=headers)  # noqa: E501

    assert response.status_code == status.HTTP_201_CREATED

def test_create_user_authorized_not_admin(authorized_user_not_admin: Any) -> None:  # noqa: ANN401, D103, E501
    client, user_id = authorized_user_not_admin

    user_data = {
        "username": "test_user_shouldn't_be_created",
        "email": "test_user_created2@example.com",
        "is_superuser": True,
        "password": "string"
    }

    headers = {"Authorization": "Bearer fake-token"}

    response = client.post(f"/user/{user_id}/create/", json=user_data, headers=headers)  # noqa: E501

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_user_unauthorized(unauthorized_client: TestClient) -> None:  # noqa: D103

    user_data = {
        "username": "un_autorised_attampt_user",
        "email": "test_user_created3@example.com",
        "is_superuser": True,
        "password": "string"
    }

    headers = {"Authorization": "Bearer fake-token"}

    response = unauthorized_client.post(f"/user/{FIXED_USER_ID}/create/", json=user_data, headers=headers)  # noqa: E501

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
