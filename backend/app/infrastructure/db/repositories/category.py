from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id: str) -> list[Category]:
        result = await self.session.execute(select(Category).where(Category.user_id == user_id))
        return list(result.scalars().all())

    async def create(self, user_id: str, name: str, type: str, color: str | None = None) -> Category:
        cat = Category(user_id=user_id, name=name, type=type, color=color)
        self.session.add(cat)
        await self.session.flush()
        return cat

    async def get_by_id_for_user(self, user_id: str, category_id: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self, user_id: str, name: str, type: str, color: str | None = None
    ) -> Category:
        """Найти категорию по имени или создать."""
        result = await self.session.execute(
            select(Category).where(Category.user_id == user_id, Category.name == name)
        )
        cat = result.scalar_one_or_none()
        if cat:
            return cat
        return await self.create(user_id, name, type, color)
