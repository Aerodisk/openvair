"""ORM models of the block device module"""

import uuid

from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy.orm import registry
from sqlalchemy.dialects import postgresql

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

iscsi_interfaces = Table(
    'iscsi_interfaces',
    mapper_registry.metadata,
    Column(
        'id',
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column('inf_type', String(20)),
    Column('ip', String(40), unique=True),
    Column('port', String(20), nullable=True),
    Column('status', String(20)),
)


class ISCSIInterface:
    """ORM model for iscsi_interfaces table"""

    pass


def start_mappers() -> None:
    """Start mapping ORM models to tables on db for the block device module"""
    mapper_registry.map_imperatively(ISCSIInterface, iscsi_interfaces)
