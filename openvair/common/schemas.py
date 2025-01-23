"""Common schemas for standardizing API responses.

This module defines a generic Pydantic schema for creating consistent
API response structures across the application.

Classes:
    BaseResponse: A generic schema for API responses, supporting customizable
        data, status, and error messages.
"""

from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Generic schema for API responses.

    This schema is designed to standardize API responses by including
    a status, optional data, and an optional error message.

    Attributes:
        status (str): The status of the response (e.g., "success", "error").
        data (Optional[T]): The data payload of the response, if applicable.
        error (Optional[str]): An error message, if applicable.
    """

    status: str
    data: Optional[T] = None
    error: Optional[str] = None
