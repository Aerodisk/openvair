"""Serializing data to suittable formats."""

from typing import Any, Dict

from openvair.modules.scheduler.adapters.orm import SchedulerJob


class SchedulerJobSerializer:
    """Base class for serializing methods."""

    @staticmethod
    def to_web(db_model: SchedulerJob) -> Dict[str, Any]:
        """Gathering db attributes and converting them to a json format."""
        return {
            'id': str(db_model.id),
            'name': db_model.name,
            'description': db_model.description,
            'cron_schedule': db_model.cron_schedule,
            'command': db_model.command,
            'enabled': db_model.enabled,
            'created_at': (
                db_model.created_at.isoformat() if db_model.created_at else None
            ),
            'updated_at': (
                db_model.updated_at.isoformat() if db_model.updated_at else None
            ),
            'last_run': db_model.last_run.isoformat()
            if db_model.last_run
            else None,
            'next_run': db_model.next_run.isoformat()
            if db_model.next_run
            else None,
        }

    @staticmethod
    def to_db(data: Dict[str, Any]) -> SchedulerJob:
        """Parsing json into values suitable for database attributes."""
        return SchedulerJob(**data)

    @staticmethod
    def to_domain(db_model: SchedulerJob) -> Dict[str, Any]:
        """Gathering attributes to send to domain layer for job creation."""
        return {
            'id': str(db_model.id),
            'name': db_model.name,
            'description': db_model.description,
            'cron_schedule': db_model.cron_schedule,
            'command': db_model.command,
            'enabled': db_model.enabled,
        }
