"""SQLAlchemy ORM models for the template module.

This module defines database models for the template module using SQLAlchemy
ORM.

Classes:
    - Base: Base class for ORM models.
    - Template: ORM model for the templates table.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM models.

    This class is used as a base for defining all ORM models in the template
    module.
    """


class Template(Base):
    """ORM model for the templates table.

    Attributes:
        __tablename__ (str): Name of the database table.
    """

    __tablename__ = 'templates'
