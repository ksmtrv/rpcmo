from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.forecast import ForecastResponse
from app.application.services.forecast_service import ForecastService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("", response_model=ForecastResponse)
async def get_forecast(
    days: int = Query(14, ge=1, le=90),
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = ForecastService(session)
    return await service.build_forecast(user_id, days=days)


@router.post("/recalculate", response_model=ForecastResponse)
async def recalculate_forecast(
    days: int = Query(14, ge=1, le=90),
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = ForecastService(session)
    return await service.build_forecast(user_id, days=days)
