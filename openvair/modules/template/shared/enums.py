"""Shared enums for template-related logic.

Defines enumerations used across the template module.

Enums:
    - TemplateStatus: Lifecycle states of a template.
"""

from enum import Enum


class TemplateStatus(str, Enum):
    """Represents the lifecycle status of a template.

    Values:
        - NEW: Template object created but not yet processed.
        - CREATING: Template creation is in progress.
        - AVAILABLE: Template is ready for use.
        - ERROR: Template creation or validation failed.
        - DELETING: Template is being deleted.
    """

    NEW = 'new'
    CREATING = 'creating'
    EDITING = 'editing'
    AVAILABLE = 'available'
    ERROR = 'error'
    DELETING = 'deleting'
