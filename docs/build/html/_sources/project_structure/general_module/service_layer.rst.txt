#############
service_layer
#############
Сервисный слой модуля, который объединяет инфраструктуру и ядро, реализуя
в себе бизнес-логику

exceptions.py
=============
Кастомные исключения для четкой и быстрой диагностики возможных ошибок.

manager.py
==========
Это файл, который, по сути, является демоном, который инициирует "сервер"
для общения приема сообщений в очереди сервисного слоя.

Просто передайте имя очереди для ядра в аргумент "queue_name" и SchedulerManager
в "manager".

Не забудьте сделать запустить маппинг, ведь именно на сервисном слое происходит
работа с полученными данными из БД.

.. code-block:: python

    if __name__ == '__main__':
        orm.start_mappers()
        LOG.info('Starting RPCServer for consuming')
        Protocol(server=True)(
            queue_name=API_SCHEDULER_QUEUE_NAME,
            manager=services.SchedulerManager,
        )

unit_of_work.py
===============
Контекстный менеджер для работы с транзакциями БД.

abstraction
-----------
Абстрактный unit_of_work для дальнейшей конкретной реализации, зависящей
от текущего фреймворка.

.. code-block:: python

    class AbstractUnitOfWork(metaclass=abc.ABCMeta):
        storages: repository.AbstractRepository
        storage_extra_specs: repository.AbstractRepository

        def __enter__(self) -> AbstractUnitOfWork:
            return self

        def __exit__(self, *args):
            self.rollback()

        @abc.abstractmethod
        def commit(self):
            raise NotImplementedError

        @abc.abstractmethod
        def rollback(self):
            raise NotImplementedError

session_factory
---------------
Предоставляет актуальную сессию работы с БД.

.. code-block:: python

    DEFAULT_SESSION_FACTORY = sessionmaker(
        expire_on_commit=False,
        bind=create_engine(
            config.get_postgres_uri(),
            isolation_level="REPEATABLE READ",
        )
    )

realization
-----------
Конкретная реализация абстрактного unit_of_work. В названии отражена
прямая зависимость от текущего ORM-фреймворка.
Здесь реализованы ранее описанные абстрактные методы "commit" & "rollback".
Данный unit_of_work спроектирован с принципом "явного коммита".
Поэтому после каждого успешного изменения состояния таблицы, необходимо будет
явно вызывать метод "commit".

.. code-block:: python

    class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

        def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
            self.session_factory = session_factory

        def __enter__(self):
            self.session = self.session_factory()  # type: Session
            self.storages = repository.SqlAlchemyRepository(self.session)
            return super(SqlAlchemyUnitOfWork, self).__enter__()

        def __exit__(self, *args):
            super(SqlAlchemyUnitOfWork, self).__exit__(*args)
            self.session.close()

        def commit(self):
            self.session.commit()

        def rollback(self):
            self.session.rollback()

services.py
===========
Здесь хранится SchedulerManager (название во всех модулях одинаковое),
"менеджер", реализующий взаимодействие адаптеров и ядра модуля, а также
межмодульное взаимодействие.

После конструктора класса, который объединяет в себе большое количество структур
модуля, идет описание методов для работы с модулем.

.. code-block:: python

    class SchedulerManager:

        def __init__(self):
            self.uow = unit_of_work.SqlAlchemyUnitOfWork()
            self.factory = model.StorageFactory()
            self.core_rpc = Protocol(client=True)(SCHEDULER_CORE_QUEUE_NAME)
            self.scheduler_rpc = Protocol(client=True)(API_SCHEDULER_QUEUE_NAME)

        def get_storage(self, data: dict) -> dict:
            """
            The function gets a storage id from the request, gets the storage
            from the database, and returns the storage

            Args:
              data (dict): dict - the data that came from the client

            Returns:
              A dict with the storage information.
            """
            LOG.info("Scheduler start handling response on get storage.")
            storage_id = data.pop('storage_id', None)
            LOG.debug("Get storage id from request: %s." % storage_id)
            if not storage_id:
                message = (f"Incorrect arguments were received "
                           f"in the request get volume: {data}.")
                LOG.error(message)
                raise exceptions.StorageAttributeError(message)
            with self.uow:
                db_storage = self.uow.storages.get(storage_id)
                web_storage = DataSerializer.to_web(db_storage)
                LOG.debug("Got storage from db: %s." % web_storage)
            LOG.info("Scheduler method get storage was successfully processed")
            return web_storage

