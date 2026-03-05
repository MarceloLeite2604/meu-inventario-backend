import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

alembic_configuration = context.config

if alembic_configuration.config_file_name is not None:
    fileConfig(alembic_configuration.config_file_name)

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.models import Base  # noqa: E402

target_metadata = Base.metadata

_DATABASE_URL: str = (
    os.environ.get("MNZ_PB_DATABASE_URL")
    or alembic_configuration.get_main_option("sqlalchemy.url")
    or ""
)

if not _DATABASE_URL:
    raise ValueError("DATABASE_URL must be set via MNZ_PB_DATABASE_URL or sqlalchemy.url in alembic.ini")


def run_migrations_offline() -> None:
    context.configure(
        url=_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(_DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
