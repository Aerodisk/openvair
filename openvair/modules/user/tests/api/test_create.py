from typing import Any, List # noqa: D100

from uuid import uuid4
from fastapi import status
import pytest
from fastapi.testclient import TestClient


user_data = {
        "username": "test_user_created22222",
        "email": "test_user_created222222@example.com",
        "is_superuser": True,
        "password": "string"
    }

def test_create_user_authorized_admin(client_with_auth_admin: Any, user_id: str) -> None:  # noqa: ANN401, D103

    user_data.pop("email", None)
    response = client_with_auth_admin.post(f"/user/{user_id}/create/", json=user_data)  # noqa: E501
    assert response.status_code == status.HTTP_201_CREATED


def test_create_user_authorized_not_admin(client_with_auth_not_admin: TestClient, user_id: str) -> None:  # noqa: ANN401, D103, E501

    user_data.update({"username": "test_user_shouldn't_be_created", "email": "test_user_created2@example.com"})

    response = client_with_auth_not_admin.post(f"/user/{user_id}/create/", json=user_data)  # noqa: E501
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_user_unauthorized(unauthorized_client: TestClient, user_id: str) -> None:  # noqa: D103

    user_data.update({"username": "un_autorised_attampt_user", "email": "test_user_created3@example.com"})

    response = unauthorized_client.post(f"/user/{user_id}/create/", json=user_data)  # noqa: E501
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_user_random_uuid(client_with_auth_not_admin: TestClient) -> None:  # noqa: D103

    user_data.update({"username": "un_autorised_attampt_user2", "email": "test_user_created4@example.com"})

    response = client_with_auth_not_admin.post(f"/user/{str(uuid4())}/create/", json=user_data)  # noqa: E501
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'missing_field', ['username', 'email', 'is_superuser', 'password']
)
def test_missing_fields(client_with_auth_admin: TestClient, user_id: str, missing_field: str) -> None:  # noqa: ANN401, D103

    user_data.update({"username": "un_autorised_attampt_user4", "email": "test_user_created6@example.com"})
    incorrect_data = user_data.copy()
    incorrect_data.pop(missing_field)

    response = client_with_auth_admin.post(f"/user/{user_id}/create/", json=incorrect_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# @pytest.mark.parametrize(
#     'wrong_params', [
#         ["email", "qwerty"],
#         ["username", 22],
#         ["isadmin", "admin"],
#         ["password", True]
#     ]
# )
# def test_incorrect_fields(client_with_auth_admin: TestClient, user_id: str, wrong_params: Any) -> None:  # noqa: ANN401, D103

#     user_data.update({"username": "un_autorised_attampt_user44", "email": "test_user_creat4ed6@example.com"})
#     incorrect_data = user_data.copy()
#     incorrect_data.update({wrong_params[0], wrong_params[1]})

#     response = client_with_auth_admin.post(f"/user/{user_id}/create/", json=incorrect_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
