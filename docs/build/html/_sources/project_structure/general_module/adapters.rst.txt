########
adapters
########
Директория, хранящая в себе реализацию взаимодействия с инфраструктурой проекта.
В типичном случае, с базой данных.

orm.py
======
Здесь с помощью ORM-фреймворка реализуются объекты хранения в базе данных
и сущности ЯП, на которые будут "завязаны" данные из таблиц БД.
В принципе,
структура и назначение этого файла должны быть знакомы многим разработчикам.
Но чаще всего
в проектах с плоской структурой или проектах на базе MVC-фреймворках этот
файл называют "models.py". Мы осознано пошли на изменение его названия,
чтобы не пересекаться с понятиями "Моделей" из предметно-ориентированной
архитектуры.

.. important::
   В проекте мы придерживаемся императивного стиля работы с объектами БД.
   Это значит, что в ходе работы необходимо явно указывать объект, на который
   будет произведен "маппинг" соответствующей сущности из БД и также явно
   этот "маппинг" запустить.

metadata
--------
Инициализируем объект метаданных, информация из которого будет в дальнейшем
использована в миграциях.

.. code-block:: python

   metadata = MetaData()
   mapper_registry = registry(metadata=metadata)

tables
------
Тут происходит описание структуры хранения данных в таблицах БД, включая
ключи связи таблиц друг с другом.

.. code-block:: python

   storages = Table(
       'storages', mapper_registry.metadata,
       Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
       Column('name', String(60)),
       Column('description', String(255)),
       Column('storage_type', String(30), nullable=False),
       Column('initialized', Boolean, default=False),
       Column('status', String(30), nullable=False),
      )

   storage_extra_specs = Table(
       'storage_extra_specs', mapper_registry.metadata,
       Column('id', Integer, primary_key=True),
       Column('key', String(60)),
       Column('value', String(155)),
       Column('storage_id', postgresql.UUID(as_uuid=True), ForeignKey('storages.id')),
   )

objects
-------
Здесь создаются сущности ЯП, на которые в дальнейшем будет производиться
маппинг данных из БД, и которые, в свою очередь, и будут использоваться в работе проекта.

.. code-block:: python

   class Storage:
       pass


   class StorageExtraSpecs:
       """
       Table where data stores like a key value.
       If storage came with specs like ip: 0.0.0.0 and path: /nfs/data this specs
       will insert into table in current format:

       id    |    key    |    value    |    storage_id
       -----------------------------------------------
       1     |    ip     |   0.0.0.0   |    UUID(1)
       -----------------------------------------------
       2     |   path    |  /nfs/data  |    UUID(1)
       -----------------------------------------------
       """
       pass

mapping
-------
В конце файла должна присутствовать функция "start_mappers". Именно, с ее помощью,
осуществляется маппинг данных. Эта функция в дальнейшем запускается
сервисом-планировщиком.

.. code-block:: python

   def start_mappers():

       mapper_registry.map_imperatively(
           Storage,
           storages,
           properties={
               'extra_specs': relationship(
                   StorageExtraSpecs,
                   backref='storage',
                   uselist=True
               ),
           }
       )
       mapper_registry.map_imperatively(StorageExtraSpecs, storage_extra_specs)

repository.py
=============
В данном файле хранятся абстракции и реализации паттерна "Репозиторий".
Репозиторий необходим для выполнения базовых операций над данными таблицы.

abstractions
------------
Здесь описана абстракция репозитория, которая выполняет роль интерфейса для
конкретного репозитория, а также служит дальнейшей зависимостью на уровне сервисного слоя.
В данном абстрактном репозитории описаны базовые методы взаимодействия с
таблицами БД, очень схожие с принципом CRUD.


.. code-block:: python

   class AbstractRepository(metaclass=abc.ABCMeta):
       def __init__(self):
           ...

   # Storage

       def add(self, storage: Storage):
           self._add(storage)

       def get(self, storage_id: UUID) -> Storage:
           storage = self._get(storage_id)
           return storage

       def get_all(self) -> List:
           storages = self._get_all()
           return storages

       def delete(self, storage_id: UUID):
           self._delete(storage_id)

       @abc.abstractmethod
       def _add(self, storage: Storage):
           raise NotImplementedError

       @abc.abstractmethod
       def _get(self, storage_id: UUID) -> Storage:
           raise NotImplementedError

       @abc.abstractmethod
       def _get_all(self) -> List:
           raise NotImplementedError

       @abc.abstractmethod
       def _delete(self, specs):
           raise NotImplementedError

   # StorageExtraSpecs

       def get_extra_specs(self, storage_id: UUID) -> StorageExtraSpecs:
           extra_specs = self._get_extra_specs(storage_id)
           return extra_specs

       def delete_extra_specs(self, storage_id: UUID):
           self._delete_extra_specs(storage_id)

       def filter_extra_specs(self, all: bool = True, **kwargs):
           extra_specs = self._filter_extra_specs(all, **kwargs)
           return extra_specs

       @abc.abstractmethod
       def _get_extra_specs(self, storage_id: UUID) -> StorageExtraSpecs:
           raise NotImplementedError

       @abc.abstractmethod
       def _delete_extra_specs(self, storage_id: UUID):
           raise NotImplementedError

       @abc.abstractmethod
       def _filter_extra_specs(self, all: bool, **kwargs):
           raise NotImplementedError

realization
-----------
Тут создана конкретная реализация описанного выше абстрактного репозитория,
находящаяся в зависимости от фреймворка SQLAlchemy. Эту зависимость
необходимо отразить в названии.


.. code-block:: python

    class SqlAlchemyRepository(AbstractRepository):

        def __init__(self, session):
            super(SqlAlchemyRepository, self).__init__()
            self.session = session

        def _add(self, storage: Storage):
            self.session.add(storage)

        def _get(self, storage_id: str) -> Storage:
            storage = (
                self.session.query(Storage)
                .options(joinedload(Storage.extra_specs))
                .filter_by(id=storage_id)
                .one()
            )
            return storage

        def _get_all(self):
            return (
                self.session.query(Storage)
                .options(joinedload(Storage.extra_specs))
                .all()
            )

        def _delete(self, storage_id: UUID):
            return (
                self.session.query(Storage)
                .filter_by(id=storage_id)
                .delete()
            )

        def _get_extra_specs(self, storage_id):
            specs = (
                self.session.query(StorageExtraSpecs)
                .filter_by(storage_id=storage_id)
                .all()
            )
            return specs

        def _delete_extra_specs(self, storage_id):
            return (
                self.session.query(StorageExtraSpecs)
                .filter_by(storage_id=storage_id)
                .delete()
            )

        def _filter_extra_specs(self, all: bool, **kwargs):
            if all:
                return (
                    self.session.query(StorageExtraSpecs)
                    .filter_by(**kwargs)
                    .all()
                )
            else:
                return (
                    self.session.query(StorageExtraSpecs)
                    .filter_by(**kwargs)
                    .first()
                )

serializer.py
=============
Код, отвечающий за сериализацию и десериализацию объектов, необходимую при передаче
информации между слоями приложения.

abstraction
-----------
Интерфейс для дальнейшей реализации в конкретном сериализаторе.

.. code-block:: python

    class AbstractDataSerializer(metaclass=abc.ABCMeta):

        @classmethod
        @abc.abstractmethod
        def to_domain(cls, storage: Storage) -> dict:
            ...

        @classmethod
        @abc.abstractmethod
        def to_db(cls, data: dict, orm_class=Storage):
            ...

        @classmethod
        @abc.abstractmethod
        def to_web(cls, storage) -> dict:
            ...

realization
-----------
Конкретный сериализатор данных.

* to_domain - необходим для дальнейшей передачи в ядро модуля. Превращает структуру, полученных из БД данных, в плоский словарь.
* to_db - наоборот, создает структуру для дальнейшего сохранения в БД.
* to_web - создает удобную для валидации и передачи на фронтенд многоуровневую структуру.

.. code-block:: python

    class DataSerializer(AbstractDataSerializer):

        @classmethod
        def to_domain(cls, storage: Storage) -> dict:
            """
            It takes a storage object,
            and a list of extra specs, and returns a dictionary of the storage
            object with the extra specs added to it

            Args:
              cls: The class that is being converted to a domain object.
              storage (Storage): Storage
              extra_specs: This is a list of dictionaries that contain the extra
                specs

            Returns:
              A dictionary of the storage object and the extra specs.
            """
            storage_dict = storage.__dict__.copy()
            storage_dict['id'] = str(storage_dict['id'])
            storage_dict.pop('_sa_instance_state')
            domain_extra_specs = []
            for spec in storage_dict.pop('extra_specs'):
                spec = spec.__dict__.copy()
                spec.pop('_sa_instance_state')
                domain_extra_specs.append(spec)
            # It's taking the dictionary of extra specs and adding them to the
            # storage_dict.
            storage_dict.update(**{
                        spec['key']: spec['value'] for spec in domain_extra_specs
                    })
            return storage_dict

        @classmethod
        def to_db(cls, data: dict, orm_class=Storage):
            """
            It takes a dictionary and returns an object of the class Storage

            Args:
              cls: The class that we're converting to.
              data (dict): dict
              orm_class: db table
            Returns:
              The Storage class is being returned.
            """
            orm_dict = {}
            inspected_orm_class = inspect(orm_class)
            for column in list(inspected_orm_class.columns):
                column_name = column.__dict__['key']
                orm_dict[column_name] = data.get(column_name)
            return orm_class(**orm_dict)

        @classmethod
        def to_web(cls, storage) -> dict:
            """
            It takes a storage object,
            and a list of extra specs, and returns a dictionary of the storage
            object with the extra specs added to it

            Args:
              cls: The class of the object that is being converted.
              storage: The storage object that we're converting to a dictionary.

            Returns:
              A dictionary of the storage and extra specs.
            """
            storage_dict = storage.__dict__.copy()
            storage_dict['id'] = str(storage_dict['id'])
            storage_dict.pop('_sa_instance_state')
            web_extra_specs = []
            for spec in storage_dict.pop('extra_specs'):
                spec = spec.__dict__.copy()
                spec.pop('_sa_instance_state')
                web_extra_specs.append(spec)
            # It's taking the dictionary of extra specs and adding them to the
            # storage_dict.
            storage_dict.update(
                {
                    'storage_extra_specs': {
                        spec['key']: spec['value'] for spec in web_extra_specs
                    }
                }
            )
            return storage_dict
