from typing import AsyncGenerator

from backend.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncGenerator, None]:
    async with async_session_maker() as session:
        yield session
