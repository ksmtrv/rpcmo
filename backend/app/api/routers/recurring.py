from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.recurring import RecurringRead, RecurringUpdate
from app.application.services.recurring_detection_service import RecurringDetectionService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import RecurringRepository

router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.get("/reminders", response_model=list[RecurringRead])
async def recurring_reminders(
    within_days: int = Query(14, ge=1, le=366),
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Регулярные платежи с датой следующего списания в ближайшие `within_days` дней (напоминания)."""
    end = date.today() + timedelta(days=within_days)
    repo = RecurringRepository(session)
    items = await repo.get_upcoming(user_id, end)
    return [RecurringRead.model_validate(r) for r in items]


@router.get("", response_model=list[RecurringRead])
async def list_recurring(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = RecurringRepository(session)
    items = await repo.get_by_user(user_id)
    return [RecurringRead.model_validate(r) for r in items]


@router.patch("/{recurring_id}", response_model=RecurringRead)
async def update_recurring(
    recurring_id: str,
    body: RecurringUpdate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Обновление регулярного платежа: подтверждение, деактивация, смена даты."""
    repo = RecurringRepository(session)
    r = await repo.get_by_id_for_user(user_id, recurring_id)
    if not r:
        raise HTTPException(404, "Регулярный платёж не найден")
    if body.is_confirmed is not None:
        r.is_confirmed = body.is_confirmed
    if body.is_active is not None:
        r.is_active = body.is_active
    if body.next_run_date is not None:
        r.next_run_date = body.next_run_date
    if body.name is not None:
        r.name = body.name
    await session.flush()
    return RecurringRead.model_validate(r)


@router.post("/detect")
async def detect_recurring(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = RecurringDetectionService(session)
    return await service.detect_and_create(user_id)
