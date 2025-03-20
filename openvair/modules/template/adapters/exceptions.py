"""Adapter-layer exceptions for the template module.

This module defines exceptions related to template operations at the adapter
level.

Classes:
    - TemplateNotFoundException: Exception raised when a template is not found
        in the database.
"""

from openvair.abstracts.base_exception import BaseCustomException


class TemplateNotFoundException(BaseCustomException):
    """Exception raised when a template is not found in the database."""
