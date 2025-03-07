"""Need to write"""

from uuid import uuid4

from fastapi.testclient import TestClient

from openvair.modules.volume.entrypoints.schemas import CreateVolume


def test_create_volume_success(client: TestClient) -> None:
    """Создание тома через Pydantic-модель."""
    payload = CreateVolume(
        name='test-volume',
        description='Test description',
        storage_id=uuid4(),  # Генерируем случайный UUID
        format='qcow2',
        size=10,
        read_only=False,
    )
    response = client.post(
        '/volumes/create/', json=payload.model_dump(mode='json')
    )
    assert response.status_code == 201  # noqa: PLR2004
    data: dict = response.json()
    assert data['name'] == payload.name
    assert data['size'] == payload.size


def test_create_volume_invalid_data(client: TestClient) -> None:
    """Создание тома с некорректными данными должно вернуть 422."""  # noqa: RUF002
    payload = CreateVolume(
        name='',  # Некорректное имя
        description='',
        storage_id=uuid4(),
        format='qcow2',
        size=0,  # Некорректный размер (должен быть >= 1)
        read_only=False,
    )
    response = client.post('/volumes/create/', json=payload.model_dump())
    assert response.status_code == 422  # noqa: PLR2004


def test_get_volumes(client: TestClient) -> None:
    """Проверяем, что список томов возвращается корректно."""
    response = client.get('/volumes/')
    assert response.status_code == 200  # noqa: PLR2004
    data: list = response.json()
    assert isinstance(data, list)
