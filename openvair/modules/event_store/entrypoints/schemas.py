"""Schemas for event data models.

This module defines the Pydantic models used for event data in the API.

Classes:
    Event: Pydantic model representing an event.
    CSVResponse: Pydantic model representing a CSV file response.
    DownloadResponse: Pydantic model representing a download response containing
        a CSV file.
"""

import datetime

from pydantic import BaseModel


class Event(BaseModel):
    """Pydantic model representing an event.

    Attributes:
        id (int): Unique identifier of the event.
        module (str): Name of the module where the event originated.
        object_id (str): ID of the related object.
        user_id (str): ID of the user who created the event.
        event (str): Description of the event.
        timestamp (int): Timestamp of the event occurrence.
        information (Optional[str]): Additional information about the event.
    """

    id: int
    module: str
    object_id: str
    user_id: str
    event: str
    timestamp: datetime.datetime
    information: str | None = None


class CSVResponse(BaseModel):
    """Pydantic model representing a CSV file response.

    Attributes:
        filename (str): The name of the CSV file.
        content_type (str): The content type of the file, typically 'text/csv'.
        content (List[Event]): A list of events to be included in the CSV file.
    """

    filename: str
    content_type: str
    content: list[Event]


class DownloadResponse(BaseModel):
    """Pydantic model representing a download response containing a CSV file.

    Attributes:
        file (CSVResponse): The CSV file response containing event data.
    """

    file: CSVResponse
