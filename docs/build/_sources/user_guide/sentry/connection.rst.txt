#################################
Подключение Sentry
#################################
Sentry - это платформа для управления ошибками и мониторинга 
производительности приложений. Ее основной целью является предоставление 
разработчикам инструментов для выявления, отслеживания и реагирования на 
ошибки и проблемы, возникающие в их приложениях в реальном времени. 

Регистрация аккаунта в Sentry
=============================

    1. Перейдите по ссылке для регистрации на главной странице 
       проекта Sentry https://sentry.io/welcome/

    .. figure:: /_static/img/sentry/get_started1.png
       :scale: 30 %
       :align: center
    

    2. Заполните форму регистрации заполнив все поля

    .. figure:: /_static/img/sentry/get_started2.png
       :scale: 60 %
       :align: center


    3. После успешной регистрации аккаунта переходите на страницу авторизации

    .. figure:: /_static/img/sentry/sign_in.png
       :scale: 30 %
       :align: center
    

    4. Введите свой логин и пароль

    .. figure:: /_static/img/sentry/password.png
       :scale: 60 %
       :align: center
    
Создание проекта Sentry
=======================
Создание проекта в Sentry - это первый шаг к тому, чтобы начать мониторинг
ошибок и проблем в вашем приложении. Вот пошаговая инструкция о том, как
создать проект в Sentry

    1. Перейдите на вкладку `Projects` в боковом меню

    .. figure:: /_static/img/sentry/create_project.png
       :scale: 30 %
       :align: center
    
    2. Выберите в качестве платформы FASTAPI и нажмите `"Create Project"`

    .. figure:: /_static/img/sentry/create_project2.png
       :scale: 30 %
       :align: center

    3. Скопируйте значение в строке `dsn` (то, что внутри ковычек)

    .. figure:: /_static/img/sentry/dsn_copy.png
       :scale: 30 %
       :align: center

    4. Откройте файл `prject_config.toml` в корне проекта и вставьте
       скопированную строку в качестве значения переменной `dsn`

    .. figure:: /_static/img/sentry/project_config_sentry.png
       :scale: 30 %
       :align: center
    
    5. Перезапустите приложение
        sudo systemctl restart web-app.service

    6.  Перейдите на влкадку `Issues` в боковом меню для просмотра событий

    .. figure:: /_static/img/sentry/issues_page.png
       :scale: 30 %
       :align: center

    Пример отловленой ошибки

    .. figure:: /_static/img/sentry/issues_error.png
       :scale: 30 %
       :align: center
    
    Детальный просмотр ошибки

    .. figure:: /_static/img/sentry/issues_error_detail.png
       :scale: 30 %
       :align: center
