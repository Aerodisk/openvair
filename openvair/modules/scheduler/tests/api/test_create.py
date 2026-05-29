"""API tests for creating scheduler jobs."""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.scheduler.tests.conftest import sample_job_dict


def test_create_job_success(client: TestClient) -> None:
    """Successful job creation via API."""
    payload = {
        'name': 'daily_backup',
        'description': 'System backup',
        'cron_schedule': '0 0 * * *',
        'command': '/usr/bin/backup',
        'enabled': True,
    }

    with patch(
        'openvair.modules.scheduler.entrypoints.api.SchedulerCRUD.create_job'
    ) as mock_method:
        mock_method.return_value = sample_job_dict()

        response = client.post('/scheduler/jobs', json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['data']['name'] == 'daily_backup'


def test_create_job_forbidden_command(client: TestClient) -> None:
    """Test blocking of dangerous commands (Pydantic validation)."""
    payload = {
        'name': 'malicious',
        'cron_schedule': '* * * * *',
        'command': 'rm -rf /',
        'enabled': True,
    }
    response = client.post('/scheduler/jobs', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_invalid_cron(client: TestClient) -> None:
    """Test blocking of invalid cron expressions."""
    payload = {
        'name': 'bad_cron',
        'cron_schedule': '99 99 99 99 99',
        'command': 'ls',
        'enabled': True,
    }
    response = client.post('/scheduler/jobs', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
