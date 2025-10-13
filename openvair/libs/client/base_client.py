"""Base client module for HTTP requests.

This module provides base classes for creating clients that interact with
various web services, including a general `BaseClient` for web applications
and a `PrometheusBaseClient` for interacting with Prometheus.

Classes:
    NotAuthorizedError: Custom exception for handling authorization errors.
    BaseClient: Base class for creating clients that interact with web services.
    PrometheusBaseClient: Base class for creating clients that interact with
        Prometheus.
"""

from typing import Any

import requests
from requests.adapters import HTTPAdapter

from openvair.libs.client.config import (
    get_web_app_url,
    get_default_user,
    get_prometheus_url,
)


class NotAuthorizedError(Exception):
    """Exception raised for authorization errors.

    This exception is raised when authentication fails due to incorrect
    credentials or other authorization issues.

    Args:
        message (str): A message describing the error.
    """

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the NotAuthorizedError with a message.

        Args:
            message (str): A message describing the authorization error.
            *args: Additional arguments passed to the base Exception class.
        """
        self.message = message
        super().__init__(args)


class BaseClient:
    """Base class for creating clients that interact with web services.

    This class sets up a session for making HTTP requests to a web service,
    handles authentication, and retries on failed requests.

    Attributes:
        adapter (HTTPAdapter): Adapter for configuring retries on HTTP requests.
        session (requests.Session): Session object for making HTTP requests.
        source_url (str): Base URL of the web service.
        service (str): Specific service endpoint.
        url (str): Full URL of the service endpoint.
        access_token (str): Bearer token for authorization.
        header (dict): Authorization header for HTTP requests.
    """

    def __init__(
        self, service: str, access_token: str | None = None, retries: int = 3
    ):
        """Initialize the BaseClient.

        Args:
            service (str): The specific service endpoint to interact with.
            access_token (Optional[str]): Bearer token for authorization.
                If not provided, the client will attempt to authenticate
                using default credentials.
            retries (int): The number of retries for failed HTTP requests.
                Defaults to 3.
        """
        self.adapter = HTTPAdapter(max_retries=retries)
        self.session = requests.Session()
        self.source_url = get_web_app_url()
        self.service = service
        self.url = f'{self.source_url}/{self.service}'
        self.session.mount(self.url, self.adapter)

        self.access_token = access_token if access_token else self._auth()
        self.header = {'Authorization': f'Bearer {self.access_token}'}

    def _auth(self) -> str:
        """Authenticate the client using default credentials.

        This method attempts to authenticate the client by sending a POST
        request with the default username and password to the authentication
        endpoint. If successful, it retrieves an access token.

        Returns:
            str: The retrieved access token.

        Raises:
            NotAuthorizedError: If authentication fails due to incorrect
                credentials or other issues.
        """
        login, password = get_default_user()
        auth_url = f'{self.source_url}/auth/'
        response = self.session.post(
            auth_url, data={'username': login, 'password': password}
        )
        token: str = response.json().get('access_token', '')
        if not token:
            msg = 'Incorrect login or password.'
            raise NotAuthorizedError(msg)
        return token


class PrometheusBaseClient:
    """Base class for creating clients that interact with Prometheus.

    This class sets up a session for making HTTP requests to the Prometheus
    service and configures retries for failed requests.

    Attributes:
        adpter (HTTPAdapter): Adapter for configuring retries on HTTP requests.
        session (requests.Session): Session object for making HTTP requests.
        source_url (str): Base URL of the Prometheus service.
    """

    def __init__(self, retries: int = 3):
        """Initialize the PrometheusBaseClient.

        Args:
            retries (int): The number of retries for failed HTTP requests.
                Defaults to 3.
        """
        self.adpter = HTTPAdapter(max_retries=retries)
        self.session = requests.Session()
        self.source_url = get_prometheus_url()
