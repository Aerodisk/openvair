"""API tests for retrieving scheduler jobs."""

import uuid
from unittest.mock import patch

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from openvair.modules.scheduler.tests.conftest import (
    SAMPLE_JOB_ID,
    sample_job_dict,
)


def test_get_jobs_list(client: TestClient) -> None:
    """Successful job list via GET /scheduler/jobs (pagination)."""
    with patch(
        'openvair.modules.scheduler.entrypoints.api.SchedulerCRUD.get_jobs'
    ) as mock_method:
        mock_method.return_value = []
        response = client.get('/scheduler/jobs')
        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.json()['data']


def test_get_job_by_id_success(client: TestClient) -> None:
    """Successful job retrieval by ID."""
    with patch(
        'openvair.modules.scheduler.entrypoints.api.SchedulerCRUD.get_job'
    ) as mock_method:
        mock_method.return_value = sample_job_dict(
            name='test_job',
            cron_schedule='* * * * *',
            command='ls',
        )
        response = client.get(f'/scheduler/jobs/{SAMPLE_JOB_ID}')
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['data']['id'] == SAMPLE_JOB_ID


def test_get_single_job_not_found(client: TestClient) -> None:
    """JobNotFound is translated to HTTP 404 by SchedulerCRUD."""
    fake_id = str(uuid.uuid4())
    with patch(
        'openvair.modules.scheduler.entrypoints.api.SchedulerCRUD.get_job'
    ) as mock_method:
        mock_method.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not found',
        )
        response = client.get(f'/scheduler/jobs/{fake_id}')
        assert response.status_code == status.HTTP_404_NOT_FOUND
