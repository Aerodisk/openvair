from typing import Any, Dict  # noqa: D100

import pytest
from fastapi.testclient import TestClient

from openvair.main import app
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user

FIXED_USER_ID = "0b67a738-34ff-4f9e-b0f6-5962065c0207"  # fake user_id

class FakeOAuth2Schema:  # noqa: D101
    async def __call__(self) -> str:  # noqa: D102
        return "fake-token"

def get_fake_get_current_user(isadmin: bool) -> Any:  # noqa: ANN401, D103, FBT001
    async def fake_get_current_user() -> Dict[str, Any]:
        return {
            "id": FIXED_USER_ID,
            "username": "user_for_testing",
            "email": "UUUUser@mail.com",
            "is_superuser": isadmin,
            "password": "string"
        }
    return fake_get_current_user

@pytest.fixture
def client_with_auth_admin() -> Any:  # noqa: ANN401, D103
    app.dependency_overrides[oauth2schema] = FakeOAuth2Schema()
    app.dependency_overrides[get_current_user] = get_fake_get_current_user(True)  # noqa: FBT003
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def client_with_auth_not_admin() -> None:  # type: ignore # noqa: D103
    app.dependency_overrides[oauth2schema] = FakeOAuth2Schema()
    app.dependency_overrides[get_current_user] = get_fake_get_current_user(False)  # noqa: E501, FBT003
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def authorized_user_admin(client_with_auth_admin: Any) -> Any:  # noqa: ANN401, D103
    return client_with_auth_admin, FIXED_USER_ID

@pytest.fixture
def authorized_user_not_admin(client_with_auth_not_admin: Any) -> Any:  # noqa: ANN401, D103
    return client_with_auth_not_admin, FIXED_USER_ID
