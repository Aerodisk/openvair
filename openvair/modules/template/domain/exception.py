"""Domain-specific exceptions for the template module.

This module defines exceptions related to file-level operations on templates
within the domain layer.
"""

from openvair.modules.template.shared.base_exceptions import (
    BaseTemplateDomainException,
)


class TemplateFileCreatingException(BaseTemplateDomainException):
    """Raised when a template file cannot be created."""


class TemplateFileEditingException(BaseTemplateDomainException):
    """Raised when a template file cannot be edited or renamed."""


class TemplateFileDeletingException(BaseTemplateDomainException):
    """Raised when a template file cannot be deleted."""
