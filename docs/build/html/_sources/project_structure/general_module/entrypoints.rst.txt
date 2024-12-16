###########
entrypoints
###########
"Входные ворота" модуля. Интерфейс взаимодействия с внешней средой, с
пользователем.

В данной реализации предоставляет ендпоинты фреймворка "Fastapi".

api.py
======
Здесь хранятся ендпоинты API. Для сохранения "чистоты" все операции были
вынесены в crud.py.

crud.py
=======
В этом файле описан класс Crud, в котором, исходя из названия, реализованы
базовые операции взаимодействия с сервисным слоем.

В конструкторе класса объявите клиента текущего протокола общения, указав
очередь, которая является шиной сообщений между API и сервисным слоем.

Методы класса Crud должны просто производить удаленный вызов функций
сервисного слоя.

.. code-block:: python

    class StorageCrud:
        def __init__(self):
            self.service_layer_rpc = Protocol(client=True)(API_SCHEDULER_QUEUE_NAME)

        def get_storage(self, storage_id: str) -> dict:
            LOG.info("Call scheduler on getting storage.")
            result = self.service_layer_rpc.call(
                services.SchedulerManager.get_storage.__name__,
                data_for_method={'storage_id': storage_id},
            )
            LOG.debug("Response from scheduler: %s." % result)
            if result.get('err', None):
                raise RpcCallException(result['err'])
            return result['data']

schemas.py
==========
Тут хранятся схемы валидации pydantic.
