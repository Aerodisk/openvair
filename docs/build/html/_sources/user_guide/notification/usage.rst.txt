Перед использованием
---------------------

Для использования данного функционала, необходимо указать в конфигурационном файле
проекта(project_config.toml) следующие параметры:

.. code-block:: bash

    [notifications]
        [notifications.email]
        smtp_server = 'smtp.yandex.ru'
        smtp_port = 465
        smtp_username = 'your_email@example.com'
        smtp_password = 'your_password'


После чего, нужно перезапустить сервисы данного модуля командой:

`sudo systemctl restart notification-service-layer.service notification-domain.service`