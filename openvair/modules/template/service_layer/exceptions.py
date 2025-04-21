"""Service layer exceptions for the template module.

This module defines exceptions that occur in the service layer.
"""

from openvair.modules.template.shared.base_exceptions import (
    BaseTemplateServiceLayerException,
)


class VolumeRetrievalException(BaseTemplateServiceLayerException):
    """Raised when a volume cannot be retrieved during template operations."""

    ...


class StorageRetrievalException(BaseTemplateServiceLayerException):
    """Raised when a storage entity cannot be retrieved for a template."""

    ...
