# Code convention и конфигурация линтеров Ruff и mypy

## Введение
Этот документ определяет стандарты написания кода для нашего проекта. Его цель - обеспечить единообразие, читаемость и поддерживаемость кодовой базы. Все участники проекта должны следовать этим правилам при написании нового кода и при рефакторинге существующего.

Основой нашего стиля кодирования является Google Python Style Guide. Если конкретная особенность не описана в данном документе, то ориентироваться следует на линтер Ruff. Если линтер не учитывает ситуацию, вызывающую вопросы, следует обратиться к [руководству Google](https://google.github.io/styleguide/pyguide.html).

Рекомендации в этом документе являются обязательными. Если они противоречат руководству Google, приоритет имеют правила, описанные здесь.


### Плагины
При разработке, настоятельно рекомендуется использование плагинов соответствующих инструментов в Вашей IDE. Информация по их установке указана в описании соответствующего инструмента.

## Конфигурация Ruff
Мы используем Ruff в качестве основного инструмента для линтинга и форматирования кода. Основные настройки Ruff включают:

- Целевая версия Python: 3.8
- Длина строки: 80 символов
- Ширина отступа: 4 пробела
- Стиль кавычек: одинарные кавычки
- Стиль отступов: пробелы
- Автоматическое определение окончания строки

Ruff настроен на проверку широкого спектра правил, включая стандартные проверки PEP 8, проверки импортов, документации, аннотаций типов, безопасности и различные стилистические проверки.

Для запуска проверки кода с помощью Ruff используйте следующую команду:
```bash 
ruff check .
```


Для автоматического исправления некоторых ошибок используйте:
```
ruff check --fix .
```

Для подробного ознакомление с функционалом Ruff и как работают его команды, можно ознакомиться на странице [официальной документации Ruff](https://docs.astral.sh/ruff/)

### Плагины для популярных IDE
Для удобства проверки при написании кода, рекомендуем использовать плагины, которые для официальных IDE, предварительно настроив их. 
Список поддерживаемых сред разработки и их конфигурации описана на [официальной странице](https://docs.astral.sh/ruff/integrations/)


### Справка по правилам линтера
Справку по каждому из правил, с которыми работает Ruff можно найти на [этой странице](https://docs.astral.sh/ruff/rules/)

### Игнорирование предупреждений линтера
Игнорирование предупреждений линтера допустимо в следующих случаях:

- Когда следование правилу ухудшает читаемость кода или превышена длина первой строки докуаментации, а описать локаничнее не удаётся.

Например для документации для этого в конце docstring используются аннотации:
noqa: E501, W505

E501 - line-too-long 

W505 - doc-line-too-long

```python
        """Getting all network interfaces and its extra database. VERY LONG FIRST STRING

        Args:
            is_need_filter (Optional[bool]): Flag indicating if it is
                necessary to filter interfaces or not.

        Returns:
            List of serialized dictionaries of interface's data.

        """  # noqa: E501, W505 It is not possible to describe the operation of this method more concisely
```

- Когда правило не применимо в конкретном контексте.
- Когда с точки зрения здравого смысла это имеет значение, либо этого требует конкретная реализация.

Всегда добавляйте комментарий, объясняющий, почему вы игнорируете предупреждение:

```python
# Ignoring the warning about an unused variable, as it is needed for API compatibility
unused_variable = some_function()  # noqa: F841
```

### Процесс обсуждения и изменения правил линтера
Если вы считаете, что какое-то правило линтера неуместно или требует изменения, следуйте этому процессу:

1. Создайте issue в репозитории проекта с описанием проблемы и предлагаемым решением.
2. Приведите примеры кода, демонстрирующие проблему.
3. Объясните, почему изменение правила улучшит кодовую базу.
4. Дождитесь обсуждения и консенсуса команды.
5. После одобрения, внесите изменения в конфигурацию Ruff и обновите этот документ.

---
## Конфигурация mypy
```mypy``` – это статический анализатор типов для Python, который помогает выявлять ошибки, связанные с несовместимостью типов, до выполнения кода. Мы используем mypy для строгого контроля типизации и повышения качества кода. Ниже приведены настройки mypy, используемые в проекте:

### Основные настройки
Конфигурация mypy находится в файле mypy.ini в корневом каталоге проекта и содержит следующие параметры:

```ini
[mypy]
warn_return_any = True
warn_unused_configs = True
strict_optional = True
ignore_missing_imports = True
disallow_any_unimported = True
check_untyped_defs = True
disallow_untyped_defs = True
no_implicit_optional = True
show_error_codes = True
warn_unused_ignores = True
exclude = venv|data|openvair/libs/messaging/protocol\.py
```

### Описание основных опций
**warn_return_any** = True: Предупреждает, если функция объявлена как возвращающая значение любого типа (Any). Это помогает идентифицировать места в коде, где типизация возвращаемого значения недостаточно строгая.

**warn_unused_configs** = True: Предупреждает о неиспользуемых или неправильных настройках в конфигурационном файле. Этот параметр помогает следить за чистотой и корректностью конфигурации.

**strict_optional** = True: Включает строгую проверку использования типов, которые могут быть None. Это гарантирует, что возможное значение None в типах будет корректно обрабатываться, что позволяет избежать потенциальных ошибок, связанных с несоответствием типов.

**ignore_missing_imports** = True: Игнорирует ошибки, связанные с отсутствием аннотаций типов в сторонних библиотеках. Это полезно, если проект использует библиотеки, не содержащие встроенных типов, и позволяет избежать ложных предупреждений.

**disallow_any_unimported** = True: Запрещает использование значений типа Any, импортированных из модулей, для которых отсутствует информация о типах. Это помогает сделать код более надежным и минимизировать риск ошибок, связанных с неопределенными типами.

**check_untyped_defs** = True: Анализирует функции и методы без аннотаций типов, выявляя возможные проблемы в них. Этот параметр позволяет обнаруживать ошибки в коде, даже если для некоторых функций не указаны аннотации типов.

**disallow_untyped_defs** = True: Запрещает объявления функций и методов без аннотаций типов. Это одно из ключевых правил, направленное на обеспечение строгой типизации всего кода, что значительно повышает его надежность и читаемость.

**no_implicit_optional** = True: Запрещает неявное использование Optional для аргументов, которые могут быть None. Вместо этого необходимо явно указывать Optional, что делает код более читаемым и понятным.

**show_error_codes** = True: Показывает коды ошибок вместе с сообщениями mypy. Это позволяет быстро найти подробную информацию об ошибке и понять, как ее исправить, ссылаясь на официальную документацию mypy.

**warn_unused_ignores** = True: Предупреждает, если комментарии # type: ignore используются без необходимости. Это помогает поддерживать чистоту в коде и избегать ненужных исключений из проверки типов.

**exclude = venv|data|openvair/libs/messaging/protocol\.py:** Исключает из проверки определенные файлы и каталоги, такие как виртуальное окружение (venv), данные (data) и конкретный файл (openvair/libs/messaging/protocol.py). Это позволяет сосредоточиться на проверке только тех частей кода, которые имеют значение для проекта и исключить проверку, частей, требующих рефакторинга или где динамическая типизация оправдана.

### Запуск mypy

Для запуска проверки кода с использованием настроек, описанных выше, активируйте venv проекта и выполните команду:

```
mypy .
```

### Игнорирование ошибок типов
Иногда необходимо игнорировать некоторые предупреждения mypy, например, при работе с кодом сторонних библиотек или в случаях использования динамических типов. Для этого можно использовать комментарий # type: ignore:

```python
from external_module import some_function  # type: ignore

result = some_function()  # Игнорируем предупреждение об отсутствии аннотаций типов
```

Если вы игнорируете конкретное предупреждение, всегда добавляйте пояснение к комментарию:

```python
from external_module import some_function  # type: ignore[attr-defined]  # Игнорируем, так как библиотека не предоставляет аннотацию типа
```

### Дополнительные настройки и плагины
Для удобства использования mypy можно интегрировать его с различными средами разработки (IDE), такими как PyCharm или VSCode. Это позволяет автоматически проверять типы при написании кода. Подробную информацию по интеграции можно найти в [официальной документации mypy](https://mypy.readthedocs.io/en/stable/config_file.html).

### Обсуждение и изменение правил
Если вы считаете, что какое-то правило или настройка mypy неуместны для проекта, следуйте процессу обсуждения, аналогичному тому, что используется для линтера Ruff:

Создайте issue в репозитории проекта с описанием проблемы и предложением изменения.
Приведите примеры кода, демонстрирующие проблему.
Объясните, почему изменение конфигурации mypy улучшит кодовую базу.
Дождитесь обсуждения и консенсуса команды.
После одобрения внесите изменения в конфигурацию mypy и обновите этот документ.

---
---

# Code convention и общие правила форматирования

## Длина строк и переносы

Максимальная длина строки - 80 символов. Это правило помогает сохранять код читаемым и удобным для просмотра на большинстве экранов.

Если строка превышает этот лимит, используйте переносы. Предпочтительно использовать круглые скобки для переноса строк.

Пример правильного переноса:

```python
message = (
    f"Storage status is {storage_status} "
    f"but must be in {available_statuses}"
)
```

В некоторых случаях допустимо игнорировать это правило:

Для длинных строк с URL или путями к файлам.
Для строк в многострочных строковых литералах (docstrings или комментарии).
Если вы считаете, что строку нельзя разбить без потери читаемости, обсудите это с командой. В исключительных случаях можно использовать комментарий # noqa: E501 для игнорирования предупреждения линтера:
```python
very_long_variable_name = some_long_function_call(arg1, arg2, ...)  # noqa: E501
```

Помните, что злоупотребление игнорированием правил может привести к снижению качества кода. Всегда стремитесь к соблюдению ограничения в 80 символов, когда это возможно.

## Отступы и пробелы

Используйте 4 пробела для отступов. Не используйте табуляцию.


```python
def long_function_name(
        var_one: str,
        var_two: str,
        var_three: str,
) -> None:
    print(var_one)
```

В случаае, если сигнатура метода не умещается в длину строки, то нужно использовать запятую после последнего аргумента и размещать каждый аргумент на новой строке:

```python
foo = long_function_name(
    var_one: str, 
    var_two: int,
    var_three: Dict,
    var_four: List,
) -> None:
```

## Правила импорта
### Форматы импортов
Импорты должны быть на отдельных строках:

```pyhon
# Правильно:
import os
import sys

# Неправильно:
import os, sys
```

Импорты всегда помещаются в начало файла, сразу после комментариев к модулю и docstrings, и перед глобальными переменными и константами.

Импорты должны быть сгруппированы в следующем порядке:

Стандартные библиотеки
Связанные сторонние импорты
Локальные импорты приложения/библиотеки
Вы должны поставить пустую строку между каждой группой импортов.

### Импорт исключений
Исключения из текущего слоя (например, сервисного) импортируются как просто exceptions. Исключения из пакетов иного слоя или отдельной библиотеки должны получать псевдоним с суффиксом _exc:


from openvair.libs.messaging import exceptions as msg_exc
from openvair.modules.storage.service_layer import exceptions

### Импорт множества классов

Если из пакета импортируется множество классов, то перечисляйте их в круглых скобках, с новой строки после открытия скобки и закрытием после перечисления последнего класса:

```python
from package import (
    Class1,
    Class2,
    Class3,
)
```

## Синтаксические правила
### Использование f-строк и r-строк
Для форматирования строк используйте исключительно f-строки. Не используйте метод format() или форматирование через символ %.

```python
# Правильно:
name = "Alice"
age = 30
message = f"Hello, {name}! You are {age} years old."

# Неправильно:
message = "Hello, {}! You are {} years old.".format(name, age)
message = "Hello, %s! You are %d years old." % (name, age)
```
Для регулярных выражений используйте r-строки:
```python
import re

pattern = r"\d{3}-\d{2}-\d{4}"
ssn = "123-45-6789"
if re.match(pattern, ssn):
    print("Valid SSN format")
```

### Реализация метода super()
При вызове метода суперкласса используйте super() без передачи наименования класса:

```python
class StorageServiceLayerManager(BackgroundTasks):
    def __init__(self):
        super().__init__()

class BridgePortGroup(BasePortGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

```
### Типизация (Type hints)
Обязательно используйте аннотации типов (type hints) для аргументов функций, методов и возвращаемых значений. Используйте библиотеку typing для сложных типов.

Для словарей и подобных структур не описывайте вложенные типы для входящих аргументов, но обязательно описывайте их для возвращаемых значений. Если могут быть разные типы данных, предусмотрите это в аннотации.

```python
from typing import Dict, Union

def create_partition(self, data: Dict) -> Dict[str, int]:
    # Реализация метода

def process_data(self, data: Dict) -> Dict[str, Union[str, int]]:
    # Реализация метода
```

## Правила нейминга
### Классы
Имена классов должны следовать соглашению CapWords (также известному как PascalCase):

```python
class MyClass:
    pass

class MyABCClass:
    pass
```
### Методы и функции

Имена методов и функций должны быть написаны в нижнем регистре, с подчеркиваниями между словами:

```python
def my_function():
    pass

class MyClass:
    def my_method(self):
        pass
```

### Переменные
Имена переменных также должны быть написаны в нижнем регистре, с подчеркиваниями между словами:

```python
my_variable = 5
user_name = "John"
```
### Константы
Константы должны быть написаны заглавными буквами с подчеркиваниями между словами:

```python
MAX_OVERFLOW = 100
TOTAL = 0
```

## Комментарии и документация
Комментарии должны быть полными предложениями. Если комментарий - фраза или предложение, первое слово должно быть написано с заглавной буквы, если это не имя переменной, начинающееся с нижнего регистра.

## Формирование docstring
Docstring в Python-модулях используется для документирования различных элементов: модулей, классов, функций и методов. Существуют определенные правила и рекомендации по их оформлению.

### Общие правила форматирования
- Форматирование с использованием 4 пробелов для отступов.


### Docstring модуля
Docstring модуля (.py файл) должен находиться в самом начале файла. Он должен содержать:

- Краткое описание модуля и его назначение.
- Подробное описание назначения модуля и особенностей его работы
- Описание основных классов, перечислений и других сущностей, определенных в модуле.

При формировании docstring модуля, переносы строк должны быть сделаны таким образом, чтобы каждый абзац (логическая группа предложений) был на отдельной строке. В случае переноса содержание новой строки должно выделяться табуляцией

#### Пример docstring модуля:

```python
"""Module for managing the Block Devices Service Layer.

This module defines the `BlockDevicesServiceLayerManager` class, which serves as
the main entry point for handling block device-related operations in the service
layer. The class is responsible for interacting with the domain layer and the
event store to perform various tasks, such as retrieving the host IQN and
managing ISCSI sessions.

The module also includes the `ISCSIInterfaceStatus` enum, which defines the
possible status values for an ISCSI interface, and the `CreateInterfaceInfo`
namedtuple, which is used to store information about a new ISCSI interface.

Classes:
    ISCSIInterfaceStatus: Enum representing the possible status values for an
        ISCSI interface.
    CreateInterfaceInfo: Namedtuple for storing information about a new ISCSI
        interface.
    BlockDevicesServiceLayerManager: Manager class for handling block devices
        service layer operations.
"""
```



### Docstring классов, функций и методов
Для классов, функций и методов docstring должен быть оформлен в соответствии с Google-стилем:

- Первая строка должна содержать краткое описание. Одной строкой, которая не превышает допустимую длинну строки. В случае если есть превышение на небольшое количесво символов, допустимо добавить данную строку в исключения для ruff. Но рекомендуется найти лаконичное описание для первой строки, чтобы она вписывалась в формат.
- Далее следует более подробное описание. Необходимо придерживаться длины строки, если слово не умещается, то корректно его перенести на новую строку и продолжить описание там
- Секция "Attributes" должна содержать описание атрибутов класса. Она должна быть отделена пустой строкой от предыдущего описания.
- Секции "Args", "Returns" и "Raises" должны содержать описание аргументов, возвращаемого значения и исключений соответственно. Каждая секция должна быть отделена пустой строкой.
- При описании атрибутов, аргументов и потенциальных исключений, обратите внимание на переносы, для удобства читаемости кода, перенесённая строка продолжающаяя описание конкретного элемента дополняется ещё одни отступом.

Пример:
```python
# Некорректно
"""
    ...

    Attributes:
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
        domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
        with the API service layer.

"""
# Корректно
"""
    ...

    Attributes:
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
            with the API service layer.
"""
```

#### Пример docstring класса:
```python
class BlockDevicesServiceLayerManager(BackgroundTasks):
    """Manager class for handling block devices service layer operations.

    This class is responsible for coordinating the interactions between the
    service layer and the domain layer, as well as the event store, to manage
    block device-related operations.

    Attributes:
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
            with the API service layer.
        uow (SqlAlchemyUnitOfWork): Unit of work for managing database
            transactions.
        event_store (EventCrud): Event store for handling block device-related
            events.
    """

    def __init__(self):
        """Initialize the BlockDevicesServiceLayerManager.

        This method sets up the necessary components for the
        BlockDevicesServiceLayerManager, including the RabbitMQ RPC clients,
        the unit of work, and the event store.
        """
        super().__init__()
        self.domain_rpc: RabbitRPCClient = Protocol(client=True)(
            SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        # ...

    def lip_scan(self) -> Dict:
        """Perform a Fibre Channel LIP (Loop Initialization Procedure) scan.

        This method is responsible for initiating a Fibre Channel LIP scan on
        the host system. It communicates with the domain layer to execute the
        LIP scan and returns the result.

        Returns:
            Dict: The result of the Fibre Channel LIP scan.

        Raises:
            FibreChannelLipScanException: If an error occurs during the LIP scan
                process.
        """
        # ...
```
