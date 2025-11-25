"""ORM models of the block device module"""

import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    """Base class for inheritance images and attachments tables."""

    pass


class ISCSIInterface(Base):
    """ORM model for iscsi_interfaces table"""

    __tablename__ = 'iscsi_interfaces'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    inf_type: Mapped[str] = mapped_column(String(20), nullable=True)
    ip: Mapped[str] = mapped_column(String(40), unique=True, nullable=True)
    port: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=True)
