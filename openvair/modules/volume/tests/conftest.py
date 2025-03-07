  # noqa: D100
from uuid import uuid4
from typing import TYPE_CHECKING, Generator

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from openvair.main import app
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user
from openvair.modules.volume.config import DEFAULT_SESSION_FACTORY
from openvair.modules.volume.adapters.orm import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@pytest.fixture(scope='session')
def client() -> TestClient:
    """Фикстура тестового клиента API."""
    return TestClient(app)


@pytest.fixture(scope='function', autouse=True)
def cleanup_db() -> Generator[None, None, None]:
    """Фикстура очистки БД перед каждым тестом."""
    db_session: Session = DEFAULT_SESSION_FACTORY()
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    yield
    db_session.close()


@pytest.fixture(autouse=True)
def mock_auth_dependency() -> None:
    """Заменяем `get_current_user` и `oauth2schema` в FastAPI Dependency Override."""  # noqa: E501
    app.dependency_overrides[oauth2schema] = lambda: 'mocked_token'
    app.dependency_overrides[get_current_user] = lambda token='mocked_token': {
        'id': str(uuid4()),  # Генерируем случайный UUID вместо строки
        'username': 'test_user',
        'role': 'admin',
        'token': token,
    }


@pytest.fixture(scope='session', autouse=True)
def configure_pagination() -> None:
    """Настраиваем пагинацию для тестов."""
    add_pagination(app)  # Добавляет параметры пагинации по умолчанию
