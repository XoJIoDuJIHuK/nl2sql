"""Database core functionality - engine and session management."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""


# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.get_database_url,
    echo=settings.echo_sql,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    # Optimize for async operations
    future=True,
)

# Create async session factory
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Better for async operations
    autoflush=False,  # Explicit control over flushing
)


async def get_async_session() -> AsyncSession:
    """Get a new async database session.

    Returns:
        An async SQLAlchemy session.
    """
    return async_session_maker()


async def create_all_tables():
    """Create all database tables from models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    """Drop all database tables. Use with caution!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)