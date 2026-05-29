"""API tests for deleting scheduler jobs."""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from openvair.modules.scheduler.tests.conftest import (
    SAMPLE_JOB_ID,
    sample_job_dict,
)


def test_delete_job_success(client: TestClient) -> None:
    """Successful job deletion via API."""
    with patch(
        'openvair.modules.scheduler.entrypoints.api.SchedulerCRUD.delete_job'
    ) as mock_method:
        mock_method.return_value = sample_job_dict(
            name='deleted_job',
            enabled=False,
        )

        response = client.delete(f'/scheduler/jobs/{SAMPLE_JOB_ID}')

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['data']['id'] == SAMPLE_JOB_ID
