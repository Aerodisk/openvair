"""Serializers for the scheduler module.

Converts ORM models to typed DTOs for API and domain layers.
"""

from typing import Any, Dict

from openvair.modules.scheduler.adapters.orm import SchedulerJob
from openvair.common.serialization.base_serializer import BaseSerializer
from openvair.modules.scheduler.adapters.dto.internal.models import (
    ApiSchedulerJobDTO,
    CreateSchedulerJobOrmDTO,
    DomainSchedulerJobPayloadDTO,
)


class ApiSchedulerJobSerializer(
    BaseSerializer[ApiSchedulerJobDTO, SchedulerJob]
):
    """ORM ↔ API response DTO."""

    dto_class = ApiSchedulerJobDTO
    orm_class = SchedulerJob


class DomainSchedulerJobSerializer(
    BaseSerializer[DomainSchedulerJobPayloadDTO, SchedulerJob]
):
    """ORM ↔ domain RPC payload DTO."""

    dto_class = DomainSchedulerJobPayloadDTO
    orm_class = SchedulerJob


class CreateSchedulerJobSerializer(
    BaseSerializer[CreateSchedulerJobOrmDTO, SchedulerJob]
):
    """Create payload ↔ ORM."""

    dto_class = CreateSchedulerJobOrmDTO
    orm_class = SchedulerJob


class SchedulerJobSerializer:
    """Facade kept for call sites that expect dict-based serialization."""

    @staticmethod
    def to_web(db_model: SchedulerJob) -> Dict[str, Any]:
        """Convert ORM job to JSON-serializable API dict."""
        return ApiSchedulerJobSerializer.to_dict(db_model)

    @staticmethod
    def to_db(data: Dict[str, Any]) -> SchedulerJob:
        """Build ORM job from create payload dict."""
        return CreateSchedulerJobSerializer.from_dict(data)

    @staticmethod
    def to_domain(db_model: SchedulerJob) -> Dict[str, Any]:
        """Convert ORM job to domain RPC payload dict."""
        return DomainSchedulerJobSerializer.to_dict(db_model)
