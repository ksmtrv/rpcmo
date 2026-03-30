from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import MappingTemplate


class MappingTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id: str) -> list[MappingTemplate]:
        result = await self.session.execute(
            select(MappingTemplate).where(MappingTemplate.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: object) -> MappingTemplate:
        tpl = MappingTemplate(**kwargs)
        self.session.add(tpl)
        await self.session.flush()
        return tpl
