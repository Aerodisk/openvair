######################################
Остальное содержимое каталога модуля
######################################

Рассмотрим подробнее, что еще находится в директории модуля.

config.py
=========

imports
-------
Тут импортируем конфиг, специальный утилитарный "модуль", где в
toml файле хранятся конфигурации проекта.

.. code-block:: python

    import config

queues
------
Обозначаем очереди, который будут использоваться как шины сообщений
в общении между слоями модуля.

.. code-block:: python

    API_SCHEDULER_QUEUE_NAME = 'storage_api_scheduler'
    SCHEDULER_CORE_QUEUE_NAME = 'storage_scheduler_core'

postgres_uri
------------
Функция получения адреса базы данных.

.. code-block:: python

    def get_postgres_uri():
        database = config.data.get('database', {})
        port = database.get('port', 5432)
        host = database.get('host', '0.0.0.0')
        password = database.get('password', 'aero')
        user = database.get('user', 'aero')
        db_name = database.get('db_name', 'openvair')
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

storage-core.service
====================
Демон, который будет скопирован в ходе установки в /etc/systemd/system/,
обеспечивающий непрерывную работу принимающей части протокола общения на уровне
ядра.

storage-scheduler.service
=========================
Демон, который будет скопирован в ходе установки в /etc/systemd/system/,
обеспечивающий непрерывную работу принимающей части протокола общения на уровне
сервисного слоя.
