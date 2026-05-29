"""API tests for updating scheduler jobs."""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.scheduler.tests.conftest import (
    SAMPLE_JOB_ID,
    sample_job_dict,
)


def test_update_job_name(client: TestClient) -> None:
    """Successful job update via PATCH /scheduler/jobs/{job_id}."""
    with patch(
        'openvair.modules.scheduler.entrypoints.api.SchedulerCRUD.update_job'
    ) as mock_method:
        mock_method.return_value = sample_job_dict(
            name='new_name',
            description='Updated',
            updated_at='2024-05-28T12:00:00Z',
        )

        response = client.patch(
            f'/scheduler/jobs/{SAMPLE_JOB_ID}',
            json={'name': 'new_name'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['data']['name'] == 'new_name'
