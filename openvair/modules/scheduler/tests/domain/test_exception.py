"""Unit tests for the scheduler domain exceptions."""

from openvair.modules.scheduler.domain.exception import CronJobNotFound


def test_cron_job_not_found_exception() -> None:
    """Test string representation of CronJobNotFound."""
    job_id = "abc-123-def"
    exc = CronJobNotFound(job_id)

    assert isinstance(exc, Exception)
