"""Integration tests for event store API endpoints.

Covers:
- Retrieving all events with pagination and filtration.
- Downloading events as CSV file.
- Handling empty responses.
- Unauthorized access to both endpoints.
"""

import io
import csv
from typing import Dict, List

from httpx import Response
from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


def assert_csv_events_empty(response: Response) -> None:
    """Assert that a CSV response contains only the header and no events rows.

    Args:
        response: The HTTP response object containing CSV content.
    """
    content = response.content.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == 1  # only header
    assert rows[0] == [
        'id',
        'module',
        'object_id',
        'user_id',
        'event',
        'timestamp',
        'information',
    ]


def test_get_events_success(client: TestClient, created_event: Dict) -> None:
    """Test successful retrieval of all events.

    Asserts:
    - Return 200 OK
    - Event under test is present in results.
    - Pagination structure is correct.
    """
    response = client.get('/event/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_keys = {'items', 'total', 'page', 'size'}
    assert all(key in data for key in expected_keys)
    assert len(data['items']) == 1

    event = data['items'][0]
    expected_data = {
        'module': created_event['module'],
        'object_id': created_event['object_id'],
        'user_id': created_event['user_id'],
        'event': created_event['event'],
        'information': created_event['information'],
    }
    for key, value in expected_data.items():
        assert event[key] == value


def test_get_events_empty(client: TestClient) -> None:
    """Test event retrieval when no events exist.

    Asserts:
    - Return 200 OK
    - Empty items list is returned.
    - Total count is zero.
    """
    response = client.get('/event/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['items'] == []
    assert data['total'] == 0


def test_get_events_pagination(
    client: TestClient, multiple_events: List[Dict]
) -> None:
    """Test event pagination with page and size parameters.

    Asserts:
    - Return 200 OK
    - Correct number of items per page.
    - Total count includes all events.
    """
    page = 1
    size = 2
    response = client.get(f'/event/?page={page}&size={size}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['items']) == size
    assert data['total'] == len(multiple_events)
    assert data['page'] == page
    assert data['size'] == size


def test_get_events_filtered_by_module_name(
    client: TestClient, created_event: Dict
) -> None:
    """Test filtering events by specific module name.

    Asserts:
    - Return 200 OK
    - Only events from specified module are returned.
    - Event under test is present when filtering by its module.
    """
    module_name = created_event['module']
    response = client.get(f'/event/?module_name={module_name}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data['items']) == 1
    assert data['items'][0]['module'] == module_name
    assert data['items'][0]['object_id'] == created_event['object_id']


def test_get_events_filtered_by_different_module(
    client: TestClient, created_event: Dict
) -> None:
    """Test filtering events by different module name, returns empty.

    Asserts:
    - Return 200 OK
    - No events returned when filtering.
    """
    module_name = f'not_{created_event["module"]}'
    response = client.get(f'/event/?module_name={module_name}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['items'] == []
    assert data['total'] == 0


def test_get_events_by_module_with_multiple_events(
    client: TestClient, multiple_events: List[Dict]
) -> None:
    """Test filtering events by module when multiple events exist.

    Asserts:
    - Return 200 OK
    - Only events from specified module are returned.
    - Correct count of filtered events.
    """
    test_module_name = 'test_module'
    response = client.get(f'/event/?module_name={test_module_name}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['items']) == len(multiple_events)
    assert all(event['module'] == 'test_module' for event in data['items'])


def test_get_events_with_invalid_pagination(client: TestClient) -> None:
    """Test invalid pagination parameters return 422.

    Asserts:
    - Invalid page and size values are properly validated.
    """
    response = client.get('/event/?page=-1&size=0')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_events_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized access to events endpoint.

    Asserts:
    - Unauthenticated requests return 401.
    """
    response = unauthorized_client.get('/event/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_download_events_success(
    client: TestClient, created_event: Dict
) -> None:
    """Test successful CSV download of events.

    Asserts:
    - Return 200 OK
    - Correct content type and headers.
    - CSV contains expected columns and data.
    """
    response = client.get('/event/download')
    assert response.status_code == status.HTTP_200_OK
    assert 'text/csv' in response.headers['content-type']
    assert 'filename=logs.csv' in response.headers['content-disposition']
    content = response.content.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == 1 + 1  # header + 1 row
    assert rows[0] == [
        'id',
        'module',
        'object_id',
        'user_id',
        'event',
        'timestamp',
        'information',
    ]
    data_row = rows[1]
    assert data_row[1] == created_event['module']
    assert data_row[2] == created_event['object_id']
    assert data_row[3] == created_event['user_id']
    assert data_row[4] == created_event['event']
    assert data_row[6] == created_event['information']


def test_download_events_empty(client: TestClient) -> None:
    """Test CSV download when no events exist.

    Asserts:
    - Return 200 OK
    - CSV contains only header row.
    - File is still properly formatted.
    """
    response = client.get('/event/download')
    assert response.status_code == status.HTTP_200_OK
    assert_csv_events_empty(response)


def test_download_events_filtered_by_module_name(
    client: TestClient, created_event: Dict
) -> None:
    """Test CSV download filtered by specific module name.

    Asserts:
    - Return 200 OK
    - CSV contains only events from specified module.
    - Correct event data in CSV.
    """
    module_name = created_event['module']
    response = client.get(f'/event/download?module_name={module_name}')
    assert response.status_code == status.HTTP_200_OK
    assert 'text/csv' in response.headers['content-type']
    content = response.content.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == 1 + 1  # header + 1 row
    assert rows[1][1] == module_name
    assert rows[1][2] == created_event['object_id']


def test_download_events_filtered_by_different_module(
    client: TestClient, created_event: Dict
) -> None:
    """Test CSV download filtered by different module, returns empty.

    Asserts:
    - Return 200 OK
    - CSV contains only header when no events match filter.
    """
    module_name = f'not_{created_event["module"]}'
    response = client.get(f'/event/download?module_name={module_name}')
    assert response.status_code == status.HTTP_200_OK
    assert_csv_events_empty(response)


def test_download_events_by_module_with_multiple_events(
    client: TestClient, multiple_events: List[Dict]
) -> None:
    """Test CSV download filtered by module with multiple matching events.

    Asserts:
    - Return 200 OK
    - CSV contains all events.
    - Correct number of rows including header.
    """
    response = client.get('/event/download')
    assert response.status_code == status.HTTP_200_OK
    content = response.content.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == 1 + len(multiple_events)  # header + 3 events
    assert all(row[1] == 'test_module' for row in rows[1:])  # all events


def test_download_events_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized CSV download.

    Asserts:
    - Unauthenticated download requests return 401.
    """
    response = unauthorized_client.get('/event/download')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
