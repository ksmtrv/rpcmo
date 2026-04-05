from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services.rule_conditions import matches_rule_conditions
from app.infrastructure.db.repositories import CategorizationRuleRepository


async def resolve_category_from_rules(
    session: AsyncSession,
    user_id: str,
    description: str,
    counterparty: str | None,
    direction: str,
) -> str | None:
    repo = CategorizationRuleRepository(session)
    for r in await repo.get_active_by_user(user_id):
        if matches_rule_conditions(r.conditions_json, description, counterparty, direction):
            return r.category_id
    return None
