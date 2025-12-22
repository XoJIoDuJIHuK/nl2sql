"""FastAPI dependencies for database sessions."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .core import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get a database session.

    Yields:
        AsyncSession: Database session for the request.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()