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

    async def list_by_user(self, user_id: str) -> list[CategorizationRule]:
        result = await self.session.execute(
            select(CategorizationRule)
            .where(CategorizationRule.user_id == user_id)
            .order_by(CategorizationRule.priority.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, user_id: str, rule_id: str) -> CategorizationRule | None:
        result = await self.session.execute(
            select(CategorizationRule).where(
                CategorizationRule.id == rule_id,
                CategorizationRule.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: str,
        name: str,
        priority: int,
        conditions_json: dict,
        category_id: str,
        is_active: bool = True,
    ) -> CategorizationRule:
        r = CategorizationRule(
            user_id=user_id,
            name=name,
            priority=priority,
            conditions_json=conditions_json,
            category_id=category_id,
            is_active=is_active,
        )
        self.session.add(r)
        await self.session.flush()
        return r

    async def delete(self, rule: CategorizationRule) -> None:
        self.session.delete(rule)
        await self.session.flush()
