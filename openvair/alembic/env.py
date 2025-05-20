from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from openvair.modules.event_store.adapters.orm import Base as EventBase
from openvair.modules.image.adapters.orm import Base as ImageBase
from openvair.modules.network.adapters.orm import Base as NetworkBase
from openvair.modules.storage.adapters.orm import Base as StorageBase
from openvair.modules.user.adapters.orm import Base as UserBase
from openvair.modules.virtual_machines.adapters.orm import Base as VMBase
from openvair.modules.volume.adapters.orm import Base as VolumeBase
from openvair.modules.notification.adapters.orm import Base as NotificationBase
from openvair.modules.virtual_network.adapters.orm import (
    Base as VirtualNetworkBase,
)
from openvair.modules.block_device.adapters.orm import Base as BlockDeviceBase
from openvair.modules.template.adapters.orm import Base as TemplateBase
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# config.set_section_option("alembic", "sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = orm_storage.mapper_registry.metadata
target_metadata = [
    NetworkBase.metadata,
    StorageBase.metadata,
    UserBase.metadata,
    VolumeBase.metadata,
    VMBase.metadata,
    ImageBase.metadata,
    EventBase.metadata,
    NotificationBase.metadata,
    VirtualNetworkBase.metadata,
    BlockDeviceBase.metadata,
    TemplateBase.metadata,
]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
