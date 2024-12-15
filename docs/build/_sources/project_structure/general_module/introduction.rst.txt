#################
Содержимое Модуля
#################
Пример содержимого модуля "storage".

Обратите внимание на название корневой директории модуля, оно должно быть
коротким и емким.

Стоит также обратить внимание, что вспомогательные файлы вроде сервисов или
файла конфигурации не находятся в отдельных поддиректориях.

.. note::
    В каждой директории и поддиректории присутствует файл __init__.py.
    Он не влияет на работу проекта, просто помогает интерпретатору понять, что
    конкретная папка является пакетом. Останавливаться далее на этом не будем.

* storage
    * adapters
        * __init__.py
        * orm.py
        * repository.py
        * serializer.py
    * domain
        * remotefs
            * __init__.py
            * nfs.py
        * __init__.py
        * base.py
        * manager.py
        * model.py
    * entrypoints
        * __init__.py
        * api.py
        * crud.py
        * schemas.py
    * service_layer
        * __init__.py
        * exceptions.py
        * manager.py
        * services.py
        * unit_of_work.py
    * __init__.py
    * config.py
    * storage-core.service
    * storage-scheduler.service
