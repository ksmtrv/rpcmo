from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import MappingTemplateRepository

router = APIRouter(prefix="/mapping-templates", tags=["mapping-templates"])


@router.get("")
async def list_templates(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = MappingTemplateRepository(session)
    items = await repo.get_by_user(user_id)
    return [{"id": t.id, "name": t.name, "column_map": t.column_map} for t in items]
