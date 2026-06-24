# Alembic 异步迁移环境配置
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.config import settings
from app.database import Base
from app.modules.auth.models import User  # noqa: F401
from app.modules.blog.models import Category, Post, Tag  # noqa: F401
from app.modules.resources.models import Resource, ResourceVersion, Screenshot  # noqa: F401
from app.modules.downloads.models import Folder, FileNode, FolderPermission  # noqa: F401
from app.modules.chat.models import ChatSession, ChatMessage, ChatQuota  # noqa: F401

# Alembic Config 对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 元数据，用于 autogenerate
target_metadata = Base.metadata


def _get_url() -> str:
    """从应用配置读取数据库 URL"""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """离线模式运行迁移"""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """在连接上执行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在线异步模式运行迁移"""
    connectable = create_async_engine(
        _get_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
