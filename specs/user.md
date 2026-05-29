# Open vAIR contract: user

Архитектурный контракт модуля `user` для RDE-линтера.
Источник кода: `openvair/modules/user`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/user
feature: user
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
    - name: User
      methods: []
    - name: UserSqlAlchemyRepository
      methods:
      - get_by_name
  entrypoints:
    required_classes:
    - name: BaseUser
      methods: []
    - name: Token
      methods: []
    - name: User
      methods: []
    - name: UserChangePassword
      methods: []
    - name: UserCreate
      methods: []
    - name: UserCrud
      methods:
      - auth
      - change_password
      - create_user
      - delete_user
      - get_user
      - get_users
    - name: UserDelete
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - change_password
      - create_user
      - delete_user
      - get_user
      - get_users
    - relative_path: entrypoints/auth.py
      functions:
      - auth
      - refresh_token
    required_http_endpoints:
    - method: POST
      path: /auth/
      handler: auth
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: UserCrud
      - name: form_data
        kind: depends
        required: true
        type_hint: OAuth2PasswordRequestForm
    - method: POST
      path: /auth/refresh
      handler: refresh_token
      parameters:
      - name: refresh_token
        kind: query
        required: true
        type_hint: str
    - method: GET
      path: /user/
      handler: get_user
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: UserCrud
      - name: user_dict
        kind: depends
        required: true
        type_hint: Dict
    - method: GET
      path: /user/all/
      handler: get_users
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: UserCrud
    - method: DELETE
      path: /user/{user_id}/
      handler: delete_user
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: UserCrud
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
      - name: user_id
        kind: query
        required: true
        type_hint: UUID
    - method: POST
      path: /user/{user_id}/change-password/
      handler: change_password
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: UserCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.UserChangePassword
      - name: user_id
        kind: query
        required: true
        type_hint: UUID
    - method: POST
      path: /user/{user_id}/create/
      handler: create_user
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: UserCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.UserCreate
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
      - name: user_id
        kind: query
        required: true
        type_hint: UUID
  service_layer:
    required_classes:
    - name: NotSuperUser
      methods: []
    - name: PasswordVerifyException
      methods: []
    - name: UnexpectedData
      methods: []
    - name: UserCredentialsException
      methods: []
    - name: UserDoesNotExist
      methods: []
    - name: UserExistsException
      methods: []
    - name: UserManager
      methods:
      - authenticate_user
      - change_password
      - create_user
      - delete_user
      - get_all_users
      - get_user
    - name: UserSqlAlchemyUnitOfWork
      methods: []
    - name: WrongUserIdProvided
      methods: []
```
