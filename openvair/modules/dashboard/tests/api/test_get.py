"""Integration tests for dashboard.

Covers:
- Successful return value.
- Missing required fields.
- Unauthorized access.
- RpcCallException.
- Wrong format of the output.
"""

import copy
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
from fastapi import status
from pydantic_core import ValidationError
from fastapi.testclient import TestClient

from openvair.libs.messaging.exceptions import RpcCallException
from openvair.modules.dashboard.entrypoints.schemas import NodeInfo

valid_data: Dict[str, Dict[str, Any]] = {
    'cpu': {'count': 4, 'percentage': 50.5},
    'memory': {
        'value': 16000,
        'used': 8000,
        'available': 8000,
        'percentage': 50.0,
    },
    'storage': {
        'size': 100000,
        'used': 40000,
        'free': 60000,
        'percentage': 40.0,
        'cls': 'SSD',
    },
    'iops': {'input': 100, 'output': 80, 'date': 1680000000},
    'io_latency': {'wait': 1.5, 'date': 1680000000},
    'bandwith_data': {'read': 1024.5, 'write': 512.3, 'date': 1680000000},
    'disk_data': {'read': 2048.7, 'write': 1024.1, 'date': 1680000000},
}


def test_get_dashboard_data_success(client: TestClient) -> None:
    """Test successful dashboard data retrieval with valid data."""
    with patch(
        'openvair.modules.dashboard.entrypoints.api.DashboardCrud.get_data',
        return_value=valid_data,
    ):
        response = client.get('/dashboard/')
        assert response.status_code == status.HTTP_200_OK

        validated = NodeInfo.model_validate(response.json())
        assert isinstance(validated, NodeInfo)


def test_get_node_data_unauthorized(unauthorized_client: TestClient) -> None:
    """Test unauthorized access returns HTTP 401."""
    response = unauthorized_client.get('/dashboard/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'missing_field_service_layer',
    [
        'cpu',
        'memory',
        'storage',
        'iops',
        'io_latency',
        'bandwith_data',
        'disk_data',
    ],
)
def test_get_dashboard_data_missing_required_fields(
    client: TestClient, missing_field_service_layer: str
) -> None:
    """Test dashboard data retrieval fails with missing required fields."""
    data = valid_data.copy()
    data.pop(missing_field_service_layer, None)

    with patch(
        'openvair.modules.dashboard.entrypoints.api.DashboardCrud.get_data',
        return_value=data,
    ):
        response = client.get('/dashboard/')

        assert response.status_code == status.HTTP_409_CONFLICT

        with pytest.raises(ValidationError):
            NodeInfo.model_validate(response.json())


@pytest.mark.parametrize(
    'field_path',
    [
        ['cpu', 'count'],
        ['cpu', 'percentage'],
        ['memory', 'value'],
        ['memory', 'used'],
        ['memory', 'available'],
        ['memory', 'percentage'],
        ['storage', 'size'],
        ['storage', 'used'],
        ['storage', 'free'],
        ['storage', 'percentage'],
        ['storage', 'cls'],
        ['iops', 'input'],
        ['iops', 'output'],
        ['iops', 'date'],
        ['io_latency', 'wait'],
        ['io_latency', 'date'],
        ['bandwith_data', 'read'],
        ['bandwith_data', 'write'],
        ['bandwith_data', 'date'],
        ['disk_data', 'read'],
        ['disk_data', 'write'],
        ['disk_data', 'date'],
    ],
)
def test_missing_nested_fields(
    client: TestClient, field_path: List[str]
) -> None:
    """Test that missing any nested field triggers validation failure."""
    data: Dict[str, Dict[str, Any]] = copy.deepcopy(valid_data)
    data[field_path[0]].pop(field_path[1], None)

    with patch(
        'openvair.modules.dashboard.entrypoints.api.DashboardCrud.get_data',
        return_value=data,
    ):
        response = client.get('/dashboard/')

    assert response.status_code == status.HTTP_409_CONFLICT

    with pytest.raises(ValidationError):
        NodeInfo.model_validate(data)


@pytest.mark.parametrize(
    'invalid_response',
    [
        'just a string',
        123,
        [1, 2, 3],
        None,
    ],
)
def test_get_dashboard_data_invalid_response_format(
    client: TestClient, invalid_response: List[Any]
) -> None:
    """Test that invalid response formats cause validation error"""
    with patch(
        'openvair.modules.dashboard.entrypoints.api.DashboardCrud.get_data',
        return_value=invalid_response,
    ):
        response = client.get('/dashboard/')

        assert response.status_code == status.HTTP_409_CONFLICT

        with pytest.raises(ValidationError):
            NodeInfo.model_validate(response.json())


def test_get_dashboard_data_service_layer_error(client: TestClient) -> None:
    """Test service layer errors return HTTP 500 internal server error."""
    with patch(
        'openvair.modules.dashboard.entrypoints.crud.MessagingClient.call',
        side_effect=RpcCallException('RPC call Exception'),
    ):
        response = client.get('/dashboard/')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
