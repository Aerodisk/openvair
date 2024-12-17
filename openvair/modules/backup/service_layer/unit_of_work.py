import abc
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import sessionmaker
from typing_extensions import Self

from openvair.modules.backup.adapters.repository import SqlAlchemyRepository
from openvair.modules.backup.config import DEFAULT_SESSION_FACTORY

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    def __enter__(self) -> Self:
        """Enter the unit of work context."""
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the unit of work context, rolling back if necessary."""
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory
        self.session: Session


    def __enter__(self) -> Self:
        self.session = self.session_factory()
        self.repository = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
