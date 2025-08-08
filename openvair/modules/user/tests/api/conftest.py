from typing import Any, Dict  # noqa: D100

import pytest
from fastapi.testclient import TestClient

from openvair.main import app
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user

from uuid import uuid4


@pytest.fixture(scope='session')
def user_id() -> str:
    return str(uuid4())

class FakeOAuth2Schema:
    async def __call__(self):
        return "fake-token"


def get_fake_get_current_user(isadmin: bool) -> Any:  # noqa: ANN401, D103, FBT001
    async def fake_get_current_user(user_id: str) -> Dict[str, Any]:
        return {
            "id": user_id,
            "username": "user_for_testing",
            "email": "UUUUser@mail.com",
            "is_superuser": isadmin,
            "password": "string"
        }
    return fake_get_current_user

@pytest.fixture
def client_with_auth_admin(client: TestClient) -> Any:
    app.dependency_overrides[oauth2schema] = FakeOAuth2Schema()
    app.dependency_overrides[get_current_user] = get_fake_get_current_user(True)  # noqa: FBT003
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def client_with_auth_not_admin(client: TestClient) -> None:  # type: ignore # noqa: D103
    app.dependency_overrides[oauth2schema] = FakeOAuth2Schema()
    app.dependency_overrides[get_current_user] = get_fake_get_current_user(False)  # noqa: E501, FBT003
    yield client
    app.dependency_overrides.clear()
