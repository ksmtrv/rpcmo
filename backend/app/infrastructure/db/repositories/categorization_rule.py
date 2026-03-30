from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import CategorizationRule


class CategorizationRuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_by_user(self, user_id: str) -> list[CategorizationRule]:
        result = await self.session.execute(
            select(CategorizationRule)
            .where(CategorizationRule.user_id == user_id)
            .where(CategorizationRule.is_active == True)
            .order_by(CategorizationRule.priority.desc())
        )
        return list(result.scalars().all())
