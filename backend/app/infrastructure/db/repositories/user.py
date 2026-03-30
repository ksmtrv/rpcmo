from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_local_user(self) -> User:
        result = await self.session.execute(select(User).where(User.email.is_(None)).limit(1))
        user = result.scalar_one_or_none()
        if user:
            return user
        user = User(email=None, settings={})
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
