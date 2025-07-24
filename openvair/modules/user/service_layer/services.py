"""Module for managing user-related operations in the service layer.

This module provides functionality for handling user operations such as
authentication, creation, deletion, and password management. It serves as an
intermediary between the API layer and the domain layer, coordinating
user-related tasks and managing database interactions.

Classes:
    UserManager: Manager class for handling user-related operations in the
        service layer.

Named tuples:
    UserInfo: Stores information about a user, including username, hashed
        password, email, and superuser status.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List
from collections import namedtuple

from passlib import hash
from sqlalchemy import exc
from passlib.exc import MissingDigestError

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.user.service_layer import exceptions, unit_of_work
from openvair.modules.user.adapters.serializer import DataSerializer

if TYPE_CHECKING:
    from openvair.modules.user.adapters.orm import User

LOG = get_logger(__name__)


UserInfo = namedtuple(
    'UserInfo', ['username', 'hashed_password', 'email', 'is_superuser']
)


class UserManager(BackgroundTasks):
    """Manager class for handling user-related operations in the service layer.

    This class serves as the main entry point for user management operations,
    coordinating interactions between the API layer, domain layer, and database.
    It handles tasks such as user authentication, creation, deletion, and
    password management.
    """

    def __init__(self) -> None:
        """Initialize the UserManager.

        This constructor sets up the necessary components for the UserManager,
        including:
        - Initializing the parent BackgroundTasks class
        - Setting up the unit of work for database operations
        """
        super().__init__()
        self.uow = unit_of_work.UserSqlAlchemyUnitOfWork

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash the provided password using bcrypt.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return str(hash.bcrypt.hash(password))

    @staticmethod
    def _verify_password(password: str, hashed_password: str) -> bool:
        """Verify the provided password against the hashed password.

        Args:
            password (str): The password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if the password matches the hashed password, False
                otherwise.
        """
        LOG.info('Verifying password')
        try:
            is_verify: bool = hash.bcrypt.verify(password, hashed_password)
        except MissingDigestError as err:
            raise exceptions.PasswordVerifyException(str(err))
        else:
            return is_verify

    def get_user(self, data: Dict) -> Dict:
        """Retrieve a user by ID from the database.

        Args:
            data (Dict): Dict that containing ID of the user to retrieve.

        Returns:
            Dict: The user's data serialized for web response.
        """
        LOG.info('Start getting user by id from DB.')
        user_id = data.get('user_id', '')
        with self.uow() as uow:
            user: User = uow.users.get_or_fail(user_id)
            return DataSerializer.to_web(user)

    def get_all_users(self) -> List:
        """Retrieve all users from the database.

        Returns:
            List: List of serialized user data for each user.
        """
        LOG.info('Start getting all users from DB')
        with self.uow() as uow:
            users = uow.users.get_all()
            return [DataSerializer.to_web(user) for user in users]

    def authenticate_user(self, data: Dict) -> Dict:
        """Authenticate a user based on provided credentials.

        Args:
            data (Dict): The authentication data, including 'username' and
                'password'.

        Returns:
            Dict: The authenticated user's data serialized for web response.

        Raises:
            UserCredentialsException: If the credentials are incorrect.
        """
        LOG.info('Start authenticate user.')
        username: str = data.get('username', '')
        password: str = data.get('password', '')

        with self.uow() as uow:
            db_user: User = uow.users.get_by_name(username)

            if not self._verify_password(password, db_user.hashed_password):
                message = 'Wrong credentials'
                LOG.info(message)
                raise exceptions.UserCredentialsException(message)

            web_user: Dict = DataSerializer.to_web(db_user)

        LOG.info('User authentication completed successfully.')

        return web_user

    @staticmethod
    def _check_is_super_user(data: Dict) -> None:
        """Check if the user is a superuser.

        Args:
            data (Dict): The data containing user information.

        Raises:
            NotSuperUser: If the user is not a superuser.
        """
        user_data: Dict = data.get('user_data', {})
        if not user_data.get('is_superuser'):
            message = 'User is not a superuser'
            raise exceptions.NotSuperUser(message)

    @staticmethod
    def _verificate_user_id(data: Dict) -> None:
        """Verify if the provided user ID matches the current user ID.

        Args:
            data (Dict): The data containing user information and user ID.

        Raises:
            WrongUserIdProvided: If the user ID does not match the current
                user ID.
        """
        user_id: str = data.get('user_id', '')
        user_data: Dict = data.get('user_data', {})
        if user_id != user_data.get('id'):
            message = 'Provided id does not match with ' 'current user id'
            raise exceptions.WrongUserIdProvided(message)

    def _prepare_user_info(self, user_data: Dict) -> UserInfo:
        """Prepare the user information for database operations.

        Args:
            user_data (Dict): The user data.

        Returns:
            UserInfo: The prepared user information as a named tuple.
        """
        return UserInfo(
            username=user_data.get('username'),
            hashed_password=self._hash_password(user_data.get('password', '')),
            email=user_data.get('email'),
            is_superuser=user_data.get('is_superuser', False),
        )

    def create_user(self, data: Dict) -> Dict:
        """Create a new user in the database.

        Args:
            data (Dict): The data for creating the user.

        Returns:
            Dict: The created user's data serialized for web response.

        Raises:
            UserExistsException: If a user with the same username already
                exists.
        """
        LOG.info('Start creating user in db.')
        self._check_is_super_user(data)
        self._verificate_user_id(data)
        user_info: UserInfo = self._prepare_user_info(data)
        with self.uow() as uow:
            db_user: User = DataSerializer.to_db(user_info._asdict())
            try:
                uow.users.add(db_user)
                uow.commit()
                LOG.info('User was successfully created.')
            except exc.IntegrityError as _:
                message = (
                    'User with current username'
                    f" '{user_info.username}' exists."
                )
                LOG.error(message)
                raise exceptions.UserExistsException(message)
        return DataSerializer.to_web(db_user)

    def change_password(self, data: Dict) -> Dict:
        """Change the password for an existing user.

        Args:
            data (Dict): The data containing user ID and new password.

        Returns:
            Dict: The updated user's data serialized for web response.

        Raises:
            UnexpectedData: If the user ID or new password is not provided.
            UserDoesNotExist: If the user does not exist.
        """
        user_id = data.pop('user_id', '')
        new_password: str = data.pop('new_password', '')
        if not user_id:
            message = 'Got empty user_id.'
            LOG.error(message)
            raise exceptions.UnexpectedData(message)
        if not new_password:
            message = 'Got empty new password.'
            LOG.error(message)
            raise exceptions.UnexpectedData(message)
        with self.uow() as uow:
            try:
                db_user: User = uow.users.get_or_fail(user_id)
                db_user.hashed_password = self._hash_password(new_password)
            except exc.NoResultFound as _:
                message = f"User with current id {user_id} doesn't exist."
                LOG.error(message)
                raise exceptions.UserDoesNotExist(message)
            finally:
                uow.commit()
        return DataSerializer.to_web(db_user)

    def delete_user(self, data: Dict) -> Dict:
        """Delete a user from the database.

        Args:
            data (Dict): The data containing the user ID to delete.

        Returns:
            Dict: The ID of the deleted user and a success message.

        Raises:
            UserDoesNotExist: If the user does not exist.
        """
        LOG.info('Start deleting user from db.')
        self._verificate_user_id(data)
        user_id = data.get('user_id', '')
        with self.uow() as uow:
            try:
                uow.users.get_or_fail(user_id)
                uow.users.delete_by_id(user_id)
            except exc.NoResultFound as _:
                message = f"User with current id {user_id} doesn't exist."
                LOG.error(message)
                raise exceptions.UserDoesNotExist(message)
            finally:
                uow.commit()
            LOG.info('User deleted successfully')

        return {'id': user_id, 'message': 'User was successfully deleted'}
