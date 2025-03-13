"""Schemas for the template module.

This module defines Pydantic models used for data validation
and serialization in the template module.
"""

from pydantic import BaseModel


class TemplateData(BaseModel):
    """Schema representing template metadata."""

    name: str
