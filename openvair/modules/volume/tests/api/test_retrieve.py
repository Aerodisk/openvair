# noqa: D100
import uuid

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


def test_get_all_volumes(client: TestClient, test_volume: dict) -> None:
    """Test retrieving all volumes."""
    response = client.get('/volumes/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'items' in data
    assert any(v['id'] == test_volume['id'] for v in data['items'])


def test_get_volumes_by_storage_id(
    client: TestClient, test_volume: dict
) -> None:
    """Test filtering volumes by storage_id."""
    storage_id = test_volume['storage_id']
    response = client.get(f'/volumes/?storage_id={storage_id}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(volume['storage_id'] == storage_id for volume in data['items'])


def test_get_free_volumes_only(client: TestClient, test_volume: dict) -> None:
    """Test filtering only free (unattached) volumes."""
    response = client.get('/volumes/?free_volumes=true')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(volume['id'] == test_volume['id'] for volume in data['items'])


def test_get_volumes_with_pagination(
    client: TestClient,
    test_volume: dict,  # noqa: ARG001
) -> None:
    """Test pagination metadata in volumes list."""
    response = client.get('/volumes/?page=1&size=1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert 'page' in data
    assert 'size' in data
    assert data['page'] == 1
    assert data['size'] == 1


def test_get_volumes_with_nonexistent_storage(client: TestClient) -> None:
    """Test filtering volumes by non-existent storage_id returns empty list."""
    response = client.get(f'/volumes/?storage_id={uuid.uuid4()}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['items'] == []


def test_get_volumes_with_invalid_storage_id(client: TestClient) -> None:
    """Test invalid UUID in storage_id query param returns 422."""
    response = client.get('/volumes/?storage_id=not-a-uuid')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_volumes_with_invalid_free_volumes_param(
    client: TestClient,
) -> None:
    """Test invalid free_volumes query param returns 422."""
    response = client.get('/volumes/?free_volumes=maybe')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_existing_volume_by_id(
    client: TestClient, test_volume: dict
) -> None:
    """Test retrieving an existing volume by its ID."""
    volume_id = test_volume['id']
    response = client.get(f'/volumes/{volume_id}/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == volume_id
    assert data['name'] == test_volume['name']
    assert data['storage_id'] == test_volume['storage_id']


def test_get_nonexistent_volume_by_id(client: TestClient) -> None:
    """Test retrieving a volume with a valid UUID that does not exist."""
    fake_volume_id = str(uuid.uuid4())
    response = client.get(f'/volumes/{fake_volume_id}/')
    # API возвращает 200 с пустым dict — поведение зависит от реализации  # noqa: E501, RUF003, W505
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_volume_with_invalid_uuid(client: TestClient) -> None:
    """Test retrieving a volume with an invalid UUID string."""
    response = client.get('/volumes/invalid-uuid/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
