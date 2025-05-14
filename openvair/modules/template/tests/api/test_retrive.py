# noqa: D100

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


def test_get_templates_success(client: TestClient) -> None:
    """Test successful retrieval of templates.

    Asserts:
    - Response is 200 OK.
    - Response contains paginated data.
    - Response data format matches TemplateResponse model.
    """
    response = client.get('/templates/')
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'items' in data['data']
    for item in data['data']['items']:
        assert 'id' in item
        assert 'name' in item
        assert 'description' in item


def test_get_templates_empty_response(client: TestClient) -> None:
    """Test retrieval of templates when there are no templates."""
    response = client.get('/templates/')
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'items' in data['data']
    assert len(data['data']['items']) == 0
