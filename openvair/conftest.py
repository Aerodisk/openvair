from uuid import uuid4
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from openvair.main import app
from openvair.libs.log import get_logger
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user

LOG = get_logger(__name__)




@pytest.fixture(scope='session')
def client() -> Generator[TestClient, None, None]:
    """Creates FastAPI TestClient with app instance for API testing."""
    with TestClient(app=app) as client:
        LOG.info('CLIENT WAS STARTS')
        yield client
        LOG.info('CLIENT WAS CLOSED')



@pytest.fixture(autouse=True, scope='session')
def mock_auth_dependency() -> None:
    """Overrides real JWT authentication with a mocked test user."""
    LOG.info('Mocking authentication dependencies')
    app.dependency_overrides[oauth2schema] = lambda: 'mocked_token'
    app.dependency_overrides[get_current_user] = lambda token='mocked_token': {
        'id': str(uuid4()),
        'username': 'test_user',
        'role': 'admin',
        'token': token,
    }


@pytest.fixture(scope='session', autouse=True)
def configure_pagination() -> None:
    """Registers pagination support in the test app (FastAPI-pagination)."""
    add_pagination(app)
