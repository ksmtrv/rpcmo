from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import RuleSuggestion


class RuleSuggestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: str, status: str | None = None) -> list[RuleSuggestion]:
        q = select(RuleSuggestion).where(RuleSuggestion.user_id == user_id)
        if status:
            q = q.where(RuleSuggestion.status == status)
        q = q.order_by(RuleSuggestion.coverage_count.desc())
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_by_id(self, user_id: str, suggestion_id: str) -> RuleSuggestion | None:
        result = await self.session.execute(
            select(RuleSuggestion).where(
                RuleSuggestion.id == suggestion_id,
                RuleSuggestion.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def find_pending_duplicate(
        self, user_id: str, source_pattern: str, suggested_category_id: str
    ) -> RuleSuggestion | None:
        result = await self.session.execute(
            select(RuleSuggestion).where(
                RuleSuggestion.user_id == user_id,
                RuleSuggestion.source_pattern == source_pattern,
                RuleSuggestion.suggested_category_id == suggested_category_id,
                RuleSuggestion.status == "pending",
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: str,
        source_pattern: str,
        suggested_conditions_json: dict,
        suggested_category_id: str,
        coverage_count: int,
        status: str = "pending",
    ) -> RuleSuggestion:
        s = RuleSuggestion(
            user_id=user_id,
            source_pattern=source_pattern,
            suggested_conditions_json=suggested_conditions_json,
            suggested_category_id=suggested_category_id,
            coverage_count=coverage_count,
            status=status,
        )
        self.session.add(s)
        await self.session.flush()
        return s
