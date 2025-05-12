import os
import sys
from logging.config import fileConfig

from alembic import context
from database import DATABASE_URL
from dotenv import load_dotenv
from models import BaseModel
from sqlalchemy import create_engine, pool
from models import Genre, Author, Book, City, Client, Buy, BuyBook, Step, BuyStep

load_dotenv()


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
