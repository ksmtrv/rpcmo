from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import CategorizationRuleRepository

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("")
async def list_rules(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = CategorizationRuleRepository(session)
    items = await repo.get_active_by_user(user_id)
    return [{"id": r.id, "name": r.name, "priority": r.priority, "category_id": r.category_id} for r in items]
