"""Base exceptions for the template module.

This module defines common exceptions used across the template module.

Classes:
    - BaseTemplateServiceLayerException: Base exception for service layer
        errors.
    - BaseTemplateDomainException: Base exception for domain-level errors.
"""

from openvair.abstracts.base_exception import BaseCustomException


class BaseTemplateServiceLayerException(BaseCustomException):
    """Exception raised for errors occurring in the service layer."""
    ...

class BaseTemplateDomainException(BaseCustomException):
    """Base exception for errors occurring in the template domain."""
    ...
