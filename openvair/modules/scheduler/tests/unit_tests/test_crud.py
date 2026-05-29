"""Unit tests for scheduler CRUD error translation."""

from fastapi import status

from openvair.modules.scheduler.entrypoints.crud import _translate_rpc_exception
from openvair.modules.scheduler.service_layer.exceptions import (
    JobDependencyError,
)


def test_translate_job_dependency_error_to_http_400() -> None:
    """JobDependencyError from service layer maps to HTTP 400."""
    error = JobDependencyError(
        'Cannot delete enabled job. Disable job first.'
    )
    http_error = _translate_rpc_exception(error)
    assert http_error.status_code == status.HTTP_400_BAD_REQUEST
    assert 'enabled job' in http_error.detail.lower()
