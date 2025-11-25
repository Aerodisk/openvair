# Prometheus install

1. Скачть tar.gz файл с [сайта](https://prometheus.io/download/)

        Пример: prometheus-2.37.4.linux-amd64.tar.gz

2. Распаковать скаченный архив
    ```bash
	tar -xvf prometheus-2.37.4.linux-amd64.tar.gz 
    ```

3. Создать два каталога:
    - в папке `/var/db/prometheus` будет храниться база данных prometheus
    - в папке `/etc/prometheus` будут храниться конфигурационные файлы prometheus

    ```bash
    sudo mkdir -p /var/db/prometheus /etc/prometheus
    ```

4. Переходим в папку с распакованным прометеем:
    ```bash
    cd prometheus-2.37.4.linux-amd64
    ```

5. перемещаем файлы prometheus и promtool в /usr/lib/bin
    ```bash
    sudo mv prometheus promtool /usr/local/bin/
    ```

6. Перемещаем папки console/ console_libraries/ в /etc/prometheus/
    ```bash
    sudo mv consoles console_libraries /etc/prometheus/
    ```

7. Перемещаем файл prometheus.yaml в /etc/prometheus/
    ```bash
    sudo mv prometheus.yml /etc/prometheus/
    ```

8. Добавляем права на папку для нашего юзера aero
    ```bash
    sudo chown -R aero:aero /etc/prometheus/ /var/db/prometheus 
    ```

9. Архив и распакованную папку можно удалить:
    ```bash
    cd ..
    rm -rf prometheus*
    ```

10. Проверяем версию прометея:
    ```bash
    prometheus --version
    ```

11. Создадим демона для прометея:
    ```bash
    sudo vim /etc/systemd/system/prometheus.service
    ```

    и записываем туда даные:
```
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=aero
group=aero
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/db/prometheus \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.listen-address=0.0.0.0:9090 \
  --web.enable-lifecycle

[Install]
WantedBy=multy-user.target
```

12. Добавляем автозапуск демона:
    ```bash
    sudo systemctl enable prometheus.service
    ```

13. Запускаем сервис:
    ```bash
    sudo systemctl start prometheus.service
    ```

14. Проверяем что все сработало:
    ```bash
    sudo systemctl status prometheus.service
    ```

    так же проверим вебку: [0.0.0.0:9090](http://0.0.0.0:9090)

---

# Node_exporter install

1. Скачиваем node_exporter с того же [сайта](https://prometheus.io/download/)
        
        Пример: node_exporter-1.4.0.linux-amd64.tar.gz

2. Распаковываем скачанный архив:
    ```bash
    tar -xvf node_exporter-1.4.0.linux-amd64.tar.gz
    ```

3. Заходим в распакованную папку
    ```bash
    cd node_exporter-1.4.0.linux-amd64
    ```

4. Перемещаем папку node_exporter в /etc/local/bin/
    ```bash
    sudo mv node_exporter /usr/local/bin 
    ```

5. Проверяем что все заработало:
    ```bash
    node_exporter --help
    ```

6. Создадим демона для данного сервиса:
    ```bash
    sudo vim /etc/systemd/system/node_exporter.service
    ```

    и запишем туда:
```
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=aero
group=aero
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/node_exporter \
  --collector.logind

[Install]
WantedBy=multy-user.target
```

7. Добавляем сервис в автозапуск:
    ```bash
    sudo systemctl enable node_exporter.service
    ```

8. Стартуем сервис:
    ```bash
    sudo systemctl start node_exporter.service
    ```

9. Добавляем job_name в прометей:
    ```bash
    sudo vim /etc/prometheus/prometheus.yml
    ```

    дописываем в конце файла новый job_name:
```bash
  - job_name: "node_exporter"
    static_configs:
      - targets: ["localhost:9100"]
```

10. Проверяем что prometheus.yaml конфиг рабочий:
    ```bash
    promtool check config /etc/prometheus/prometheus.yml
    
    # SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax
    ```

11. Перезагружаем прометей:
    ```bash
    curl -X POST http://localhost:9090/-/reload
    ```
    
    теперь в Status->Targets прометея будет, помимо стандартного, node_exporter,
    который будет отдавать метрики.


