"""User CRUD operations through the service layer.

This module defines the `UserCrud` class, which acts as an intermediary
between the API layer and the service layer. It provides methods for
performing CRUD operations related to users, including creating, retrieving,
updating, and deleting user records. It also handles user authentication.

Classes:
    UserCrud: A class that provides methods for user management and
        authentication by interacting with the service layer.

Methods:
    - get_user(user_id: str) -> Dict: Retrieves user information by user ID.
    - create_user(data: Dict, user_id: str, user_data: Dict) -> Dict: Creates
        a new user.
    - change_password(user_id: str, data: Dict) -> Dict: Changes the password
        for a user.
    - delete_user(user_id: str, user_data: Dict) -> Dict: Deletes a user.
    - auth(username: str, password: str) -> Dict: Authenticates a user and
        returns a token.
"""

from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.user.config import USER_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.user.service_layer import services

LOG = get_logger(__name__)


class UserCrud:
    """A class for user-related CRUD operations using a service layer.

    This class communicates with the service layer to perform user
    management operations such as getting, creating, updating, and
    deleting users, as well as handling authentication.

    Methods:
        get_user(user_id: str) -> Dict: Retrieves user information by user ID.
        create_user(data: Dict, user_id: str, user_data: Dict) -> Dict: Creates
            a new user.
        change_password(user_id: str, data: Dict) -> Dict: Changes the password
            for a user.
        delete_user(user_id: str, user_data: Dict) -> Dict: Deletes a user.
        auth(username: str, password: str) -> Dict: Authenticates a user and
            returns a token.
    """

    def __init__(self):
        """Initialize the UserCrud class.

        Creates a connection to the service layer
        """
        self.service_layer_rpc = Protocol(client=True)(
            USER_SERVICE_LAYER_QUEUE_NAME
        )

    def get_user(self, user_id: str) -> Dict:
        """Retrieve user information by user ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            Dict: The user information.
        """
        LOG.info(f'Call service layer on getting user by ID: {user_id}')
        return self.service_layer_rpc.call(
            services.UserManager.get_user.__name__,
            data_for_method=user_id,
        )

    def create_user(
        self,
        data: Dict,
        user_id: str,
        user_data: Dict,
    ) -> Dict:
        """Create a new user.

        Args:
            data (Dict): The user data for creation.
            user_id (str): The ID of the current user.
            user_data (Dict): The data of the current user.

        Returns:
            Dict: The created user information.
        """
        data.update({'user_id': user_id, 'user_data': user_data})
        return self.service_layer_rpc.call(
            services.UserManager.create_user.__name__,
            data_for_method=data,
        )

    def change_password(self, user_id: str, data: Dict) -> Dict:
        """Change the password for a user.

        Args:
            user_id (str): The ID of the user whose password is being changed.
            data (Dict): The new password data.

        Returns:
            Dict: The result of the password change operation.
        """
        data.update({'user_id': user_id})
        return self.service_layer_rpc.call(
            services.UserManager.change_password.__name__,
            data_for_method=data
        )

    def delete_user(
        self,
        user_id: str,
        user_data: Dict,
    ) -> Dict:
        """Delete a user.

        Args:
            user_id (str): The ID of the user to delete.
            user_data (Dict): The data of the current user.

        Returns:
            Dict: The result of the delete operation.
        """
        return self.service_layer_rpc.call(
            services.UserManager.delete_user.__name__,
            data_for_method={'user_id': user_id, 'user_data': user_data},
        )

    def auth(self, username: str, password: str) -> Dict:
        """Authenticate a user and return a token.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            Dict: A dictionary containing authentication tokens.
        """
        return self.service_layer_rpc.call(
            services.UserManager.authenticate_user.__name__,
            data_for_method={
                'username': username,
                'password': password,
            },
        )
