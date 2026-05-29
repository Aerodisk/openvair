"""Unit tests for the BaseScheduler interface."""

from typing import Any, Dict, Optional

from openvair.modules.scheduler.domain.base import BaseScheduler


class DummyScheduler(BaseScheduler):
    """Dummy implementation of BaseScheduler for interface testing."""

    def create(self, creation_data: Dict[str, Any]) -> Dict[str, Any]: # noqa: ARG002
        """Job creation."""
        return {"status": "created"}

    def get(self, data: Dict[str, Any]) -> Dict[str, Any]: # noqa: ARG002
        """Retrieve job."""
        return {"status": "retrieved"}

    def delete(self, data: Dict[str, Any]) -> None:
        """Delete job."""
        pass

    def list_all(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: # noqa: ARG002
        """Get list of jobs."""
        return {"jobs": []}

    def edit(self, editing_data: Dict[str, Any]) -> Dict[str, Any]: # noqa: ARG002
        """Edit job."""
        return {"status": "edited"}


def test_base_scheduler_instantiation() -> None:
    """Test that BaseScheduler can be properly subclassed."""
    scheduler = DummyScheduler()
    assert isinstance(scheduler, BaseScheduler)

    result = scheduler.list_all()
    assert result == {"jobs": []}
