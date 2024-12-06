"""Pydantic schemas for notification API.

This module defines the Pydantic models used for validation and serialization
of notification data in the API.

Classes:
    - Notification: Schema for notification data used in the API.
"""

from typing import List, Optional

from pydantic import EmailStr, BaseModel, field_validator


class Notification(BaseModel):
    """Schema for notification data.

    This schema defines the structure and validation rules for notification
    data sent to and received from the API.
    """

    msg_type: str
    recipients: Optional[List[EmailStr]] = None
    subject: str
    message: str

    @field_validator('msg_type')
    @classmethod
    def msg_type_validator(cls, value: str) -> str:
        """Validate the `msg_type` field.

        This method ensures that the `msg_type` field is either 'email' or
        'sms'.

        Args:
            value (str): The value of the `msg_type` field.

        Returns:
            str: The validated value.

        Raises:
            ValueError: If the `msg_type` is not 'email' or 'sms'.
        """
        if value not in ('email', 'sms'):
            message = "msg_type must be 'email' or 'sms'"
            raise ValueError(message)
        return str(value)
