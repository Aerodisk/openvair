# Open vAIR contract: notification

Архитектурный контракт модуля `notification` для RDE-линтера.
Источник кода: `openvair/modules/notification`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/notification
feature: notification
layers:
  adapters:
    required_classes:
    - name: Base
      methods: []
    - name: DataSerializer
      methods:
      - to_db
      - to_domain
      - to_web
    - name: Notification
      methods: []
    - name: NotificationSqlAlchemyRepository
      methods: []
  domain:
    required_classes:
    - name: AbstractNotificationFactory
      methods:
      - get_notification
    - name: BaseEmailNotification
      methods:
      - send
    - name: BaseNotification
      methods:
      - send
    - name: EmailNotification
      methods:
      - send
    - name: NoRecipientsSpecifiedForEmailNotification
      methods: []
    - name: NotificationFactory
      methods:
      - get_notification
    - name: NotificationSMTPException
      methods: []
  entrypoints:
    required_classes:
    - name: Notification
      methods:
      - msg_type_validator
    - name: NotificationCrud
      methods:
      - send_notification
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - send_notification
    required_http_endpoints:
    - method: POST
      path: /notifications/send/
      handler: send_notification
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: NotificationCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.Notification
  service_layer:
    required_classes:
    - name: NotificationNotFoundError
      methods: []
    - name: NotificationServiceLayerManager
      methods:
      - send_notification
    - name: NotificationServiceNotKnown
      methods: []
    - name: NotificationSqlAlchemyUnitOfWork
      methods: []
    - name: NotificationStatus
      methods: []
```
