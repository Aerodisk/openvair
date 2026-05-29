"""Unit tests for the CronJobScheduler domain class."""

import uuid
import datetime
from unittest.mock import MagicMock

import pytest

from openvair.modules.scheduler.domain.exception import CronJobNotFound
from openvair.modules.scheduler.domain.cron_jobs.cron_job import (
    CronJobScheduler,
)


def test_create_job_success(mock_cron_tab: MagicMock) -> None:
    """Test successful job creation in the crontab."""
    scheduler = CronJobScheduler(cron_obj=mock_cron_tab)
    job_id = str(uuid.uuid4())

    creation_data = {
        "id": job_id,
        "name": "Domain Test Job",
        "cron_schedule": "* * * * *",
        "command": "/usr/bin/backup",
        "description": "Test backup"
    }

    mock_item = MagicMock()
    mock_cron_tab.new.return_value = mock_item

    result = scheduler.create(creation_data)

    assert "job_id" in result
    mock_cron_tab.new.assert_called_once()
    mock_item.setall.assert_called_once_with("* * * * *")


def test_get_job_success(mock_cron_tab: MagicMock) -> None:
    """Test successful retrieval and enrichment of a job."""
    scheduler = CronJobScheduler(cron_obj=mock_cron_tab)
    job_id = str(uuid.uuid4())

    mock_item = MagicMock()
    mock_item.comment = f"Description OPENVAIR_JOB_ID:[{job_id}]"
    mock_item.command = "ls"
    mock_item.slices = "0 0 * * *"
    mock_item.is_enabled.return_value = True

    mock_schedule = MagicMock()
    mock_schedule.get_prev.return_value = datetime.datetime.now()
    mock_schedule.get_next.return_value = datetime.datetime.now()
    mock_item.schedule.return_value = mock_schedule

    mock_cron_tab.__iter__.return_value = [mock_item]

    result = scheduler.get({"id": job_id, "name": "DB Name"})

    assert str(result["id"]) == job_id
    assert result["command"] == "ls"
    assert result["name"] == "DB Name"
    assert result["enabled"] is True


def test_get_job_not_found(mock_cron_tab: MagicMock) -> None:
    """Test getting a non-existent job raises the correct exception."""
    scheduler = CronJobScheduler(cron_obj=mock_cron_tab)
    mock_cron_tab.__iter__.return_value = []

    with pytest.raises(CronJobNotFound):
        scheduler.get({"id": str(uuid.uuid4())})


def test_delete_job_success(mock_cron_tab: MagicMock) -> None:
    """Test successfully deleting a job from the crontab."""
    scheduler = CronJobScheduler(cron_obj=mock_cron_tab)
    job_id = str(uuid.uuid4())

    mock_item = MagicMock()
    mock_item.comment = f"Test OPENVAIR_JOB_ID:[{job_id}]"
    mock_cron_tab.__iter__.return_value = [mock_item]

    scheduler.delete({"job_id": job_id})

    mock_cron_tab.remove.assert_called_once_with(mock_item)


def test_edit_job_success(mock_cron_tab: MagicMock) -> None:
    """Test editing an existing job's parameters."""
    scheduler = CronJobScheduler(cron_obj=mock_cron_tab)
    job_id = str(uuid.uuid4())

    mock_item = MagicMock()
    mock_item.comment = f"Old Desc OPENVAIR_JOB_ID:[{job_id}]"
    mock_item.command = "/usr/bin/backup"
    mock_item.is_enabled.return_value = True

    mock_schedule = MagicMock()
    mock_schedule.get_prev.return_value = datetime.datetime.now()
    mock_schedule.get_next.return_value = datetime.datetime.now()
    mock_item.schedule.return_value = mock_schedule

    mock_cron_tab.__iter__.return_value = [mock_item]

    edit_data = {
        "id": job_id,
        "command": "/usr/bin/backup",
        "enabled": False,
        "cron_schedule": "0 12 * * *"
    }

    scheduler.edit(edit_data)

    mock_item.set_command.assert_called_once_with("/usr/bin/backup")
    mock_item.enable.assert_called_once_with(False) # noqa: FBT003
    mock_item.setall.assert_called_once_with("0 12 * * *")


def test_list_all_jobs(mock_cron_tab: MagicMock) -> None:
    """Test listing all jobs and ignoring foreign cron entries."""
    scheduler = CronJobScheduler(cron_obj=mock_cron_tab)
    job_id = str(uuid.uuid4())

    mock_item = MagicMock()
    mock_item.comment = f"Desc OPENVAIR_JOB_ID:[{job_id}]"
    mock_item.command = "/usr/bin/backup"
    mock_item.is_enabled.return_value = True
    mock_item.schedule.return_value = MagicMock()

    alien_item = MagicMock()
    alien_item.comment = "Custom sysadmin script"

    mock_cron_tab.__iter__.return_value = [mock_item, alien_item]

    result = scheduler.list_all(
        {
            "jobs_from_db": [
                {
                    "id": job_id,
                    "name": "From DB"}
                ]
            })

    assert len(result["jobs"]) == 1
    assert str(result["jobs"][0]["id"]) == job_id
    assert result["jobs"][0]["name"] == "From DB"
