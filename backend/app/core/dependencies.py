from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.infrastructure.db.repositories import UserRepository


async def get_current_user_id(session: AsyncSession = Depends(get_db)) -> str:
    if settings.local_demo_mode:
        repo = UserRepository(session)
        user = await repo.get_or_create_local_user()
        return user.id
    return "local-demo-user"
