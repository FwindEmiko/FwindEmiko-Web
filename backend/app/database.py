# 异步数据库引擎与会话管理
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

Base = declarative_base()


def _build_engine_args(url: str) -> dict:
    """根据数据库 URL 返回对应的引擎参数"""
    engine_args = {
        "echo": settings.DEBUG,
        "future": True,
    }

    if url.startswith("sqlite"):
        # SQLite 异步驱动使用 aiosqlite
        engine_args["poolclass"] = NullPool
        engine_args["connect_args"] = {"check_same_thread": False}
    else:
        # MySQL / PostgreSQL 使用连接池并保持连接活性
        engine_args["pool_pre_ping"] = True
        engine_args["pool_recycle"] = 3600

    return engine_args


engine = create_async_engine(
    settings.DATABASE_URL,
    **_build_engine_args(settings.DATABASE_URL),
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI Depends 异步会话生成器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
