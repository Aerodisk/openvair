"""Scheduler service layer configuration loader."""

import re
import getpass

import toml

from openvair.config import (
    RPC_QUEUES,
    PROJECT_ROOT,
    get_default_session_factory,
)

CONFIG_PATH = PROJECT_ROOT / 'project_config.toml'
API_SERVICE_LAYER_QUEUE_NAME: str = RPC_QUEUES.Scheduler.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = RPC_QUEUES.Scheduler.DOMAIN_LAYER
DEFAULT_SESSION_FACTORY = get_default_session_factory()


FORBIDDEN_COMMAND_PATTERNS = [
    r'\brm\s+-rf\b',     # dangerous deletion
    r'\bdd\b',           # raw disk write
    r'\bmkfs\b',         # filesystem creation
    r'\bcurl\b',         # unrestricted network calls
    r'\bwget\b',         # unrestricted downloads
]

def validate_command(command: str) -> str:
    """Centralized validation for scheduler commands.

    Checks for emptiness, forbidden dangerous utilities, and allowed syntax.
    """
    command = command.strip()
    if not command:
        msg = "Command cannot be empty or whitespace-only"
        raise ValueError(msg)

    if any(re.search(pattern, command, re.IGNORECASE)
           for pattern in FORBIDDEN_COMMAND_PATTERNS):
        msg = "Command contains forbidden or unsafe operations"
        raise ValueError(msg)

    if not re.match(r"^[a-zA-Z0-9_\-./ >&|;'\"*]+$", command):
        msg = "Command contains invalid characters"
        raise ValueError(msg)

    return command

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
_scheduler_cfg = config.get('scheduler', {})
CRON_USER: str = _scheduler_cfg.get('cron_user', getpass.getuser())


def domain_scheduler_manager_data() -> dict[str, str]:
    """RPC manager payload for SchedulerFactory on the domain queue."""
    return {'type': 'system_cron', 'user': CRON_USER}
MAX_CONCURRENT_JOBS = 10
JOB_TIMEOUT = 3600
LOG_RETENTION_DAYS = 30
