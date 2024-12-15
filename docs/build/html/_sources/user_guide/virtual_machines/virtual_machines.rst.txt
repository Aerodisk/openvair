########################
Модуль Virtual Machines
########################

Этот модуль предоставляет API для управления виртуальными машинами.

API
---

**Получение списка виртуальных машин**
---------------------------------------

.. code-block:: bash

   GET /virtual-machines/

Этот эндпоинт возвращает список всех виртуальных машин.

**Получение информации о виртуальной машине**
----------------------------------------------

.. code-block:: bash

   GET /virtual-machines/{vm_id}/

Этот эндпоинт возвращает информацию о конкретной виртуальной машине по её идентификатору.

**Создание виртуальной машины**
--------------------------------

.. code-block:: bash

   POST /virtual-machines/create/

Этот эндпоинт создает новую виртуальную машину.

    **Пример запроса**:

    .. code-block:: bash

        curl -X POST \
        http://your-api-endpoint/virtual-machines/create/ \
        -H 'Content-Type: application/json' \
        -d '{
            "name": "string",
            "description": "string",
            "os": {
                "os_type": "Linux",
                "os_variant": "Ubuntu 20.04",
                "boot_device": "cdrom",
                "bios": "LEGACY",
                "graphic_driver": "virtio"
            },
            "cpu": {
                "cores": 1,
                "threads": 1,
                "sockets": 1,
                "model": "host",
                "type": "static",
                "vcpu": "string"
            },
            "ram": {
                "size": 0
            },
            "graphic_interface": {
                "login": "string",
                "password": "string",
                "connect_type": "vnc"
            },
            "disks": {
                "attach_disks": [
                    {
                        "name": "string",
                        "emulation": "virtio",
                        "format": "qcow2",
                        "qos": {
                            "iops_read": "500",
                            "iops_write": "500",
                            "mb_read": "150",
                            "mb_write": "150"
                        },
                        "boot_order": 0,
                        "order": 0,
                        "volume_id": "string"
                    },
                    {
                        "name": "string",
                        "emulation": "virtio",
                        "format": "qcow2",
                        "qos": {
                            "iops_read": "500",
                            "iops_write": "500",
                            "mb_read": "150",
                            "mb_write": "150"
                        },
                        "boot_order": 0,
                        "order": 0,
                        "image_id": "string"
                    },
                    {
                        "name": "string",
                        "emulation": "virtio",
                        "format": "qcow2",
                        "qos": {
                            "iops_read": "500",
                            "iops_write": "500",
                            "mb_read": "150",
                            "mb_write": "150"
                        },
                        "boot_order": 0,
                        "order": 0,
                        "storage_id": "string",
                        "size": 0
                    }
                ]
            },
            "virtual_interfaces": [
                {
                    "mode": "bridge",
                    "interface": "br0",
                    "mac": "6C:4A:74:B4:FD:59",
                    "model": "virtio",
                    "order": 0
                }
            ]
        }'



**Удаление виртуальной машины**
--------------------------------

.. code-block:: bash

   DELETE /virtual-machines/{vm_id}/

Этот эндпоинт удаляет виртуальную машину по её идентификатору.

**Запуск виртуальной машины**
------------------------------

.. code-block:: bash

   POST /virtual-machines/{vm_id}/start/

Этот эндпоинт запускает виртуальную машину по её идентификатору.

**Остановка виртуальной машины**
---------------------------------

.. code-block:: bash

   POST /virtual-machines/{vm_id}/shut-off/

Этот эндпоинт останавливает виртуальную машину по её идентификатору.

**Редактирование виртуальной машины**
-------------------------------------

**Пример запроса**:

.. code-block:: bash

   curl -X POST \
   http://your-api-endpoint/virtual-machines/{vm_id}/edit/ \
   -H 'Content-Type: application/json' \
   -d '{
       "name": "edited_vm_name",
       "description": "edited_vm_description",
       "cpu": {
           "cores": 2,
           "threads": 2,
           "sockets": 2,
           "model": "host",
           "type": "static",
           "vcpu": "edited_vcpu"
       },
       "ram": {
           "size": 2048
       },
       "os": {
           "os_type": "Linux",
           "os_variant": "Ubuntu 20.04",
           "boot_device": "cdrom",
           "bios": "LEGACY",
           "graphic_driver": "virtio"
       },
       "graphic_interface": {
           "login": "edited_login",
           "password": "edited_password",
           "connect_type": "vnc"
       },
       "disks": {
           "attach_disks": [
               {
                   "name": "edited_disk_name",
                   "emulation": "virtio",
                   "format": "qcow2",
                   "qos": {
                       "iops_read": "500",
                       "iops_write": "500",
                       "mb_read": "150",
                       "mb_write": "150"
                   },
                   "boot_order": 0,
                   "order": 0,
                   "volume_id": "edited_volume_id"
               }
           ],
           "detach_disks": [
               {
                   "id": 0
               }
           ],
           "edit_disks": [
               {
                   "name": "edited_disk_name",
                   "emulation": "virtio",
                   "format": "qcow2",
                   "qos": {
                       "iops_read": "500",
                       "iops_write": "500",
                       "mb_read": "150",
                       "mb_write": "150"
                   },
                   "boot_order": 0,
                   "order": 0,
                   "id": 0
               }
           ]
       },
       "virtual_interfaces": {
           "new_virtual_interfaces": [
               {
                   "mode": "bridge",
                   "interface": "edited_br0",
                   "mac": "6C:4A:74:B4:FD:59",
                   "model": "virtio",
                   "order": 0
               }
           ],
           "detach_virtual_interfaces": [
               {
                   "id": 0
               }
           ],
           "edit_virtual_interfaces": [
               {
                   "mode": "bridge",
                   "interface": "edited_br0",
                   "mac": "6C:4A:74:B4:FD:59",
                   "model": "virtio",
                   "order": 0,
                   "id": 0
               }
           ]
       }
   }'

