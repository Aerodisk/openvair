"""Scheduler service layer configuration loader."""

from pathlib import Path

import toml

CONFIG_PATH = Path('/opt/aero/openvair/project_config.toml')

try:
    config = toml.load(CONFIG_PATH)
except FileNotFoundError:
    error_message = f'Configuration file not found: {CONFIG_PATH}'
    raise RuntimeError(error_message)

# --- RabbitMQ ---
rabbitmq_cfg = config.get('rabbitmq', {})
RABBITMQ_HOST = rabbitmq_cfg.get('host', 'localhost')
RABBITMQ_PORT = rabbitmq_cfg.get('port', 5672)
RABBITMQ_USER = rabbitmq_cfg.get('user', 'guest')
RABBITMQ_PASSWORD = rabbitmq_cfg.get('password', 'guest')

# --- Database ---
db_cfg = config.get('database', {})
DATABASE_URL = (
    f"postgresql+psycopg2://{db_cfg.get('user', 'aero')}:"
    f"{db_cfg.get('password', 'aero')}@"
    f"{db_cfg.get('host', 'localhost')}:"
    f"{db_cfg.get('port', 5432)}/"
    f"{db_cfg.get('db_name', 'openvair')}"
)

# --- Scheduler defaults ---
CRON_USER = 'openvair'
MAX_CONCURRENT_JOBS = 10
JOB_TIMEOUT = 3600
LOG_RETENTION_DAYS = 30

# --- RabbitMQ queues ---
API_SERVICE_LAYER_QUEUE_NAME = 'scheduler_api_service_layer_queue'
SERVICE_LAYER_DOMAIN_QUEUE_NAME = 'scheduler_service_layer_domain_queue'
