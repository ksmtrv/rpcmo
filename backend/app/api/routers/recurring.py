from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.recurring import RecurringRead
from app.application.services.recurring_detection_service import RecurringDetectionService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import RecurringRepository

router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.get("", response_model=list[RecurringRead])
async def list_recurring(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = RecurringRepository(session)
    items = await repo.get_by_user(user_id)
    return [RecurringRead.model_validate(r) for r in items]


@router.post("/detect")
async def detect_recurring(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = RecurringDetectionService(session)
    return await service.detect_and_create(user_id)
