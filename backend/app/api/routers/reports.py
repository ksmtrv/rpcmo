from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.reports import CashflowReport, CategoriesReport, TaxEstimateReport
from app.application.services.report_service import ReportService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/cashflow", response_model=CashflowReport)
async def cashflow_report(
    date_from: date | None = None,
    date_to: date | None = None,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Не задаём даты по умолчанию — сервис возьмёт диапазон по фактическим транзакциям
    service = ReportService(session)
    return await service.cashflow(user_id, date_from, date_to)


@router.get("/categories", response_model=CategoriesReport)
async def categories_report(
    date_from: date | None = None,
    date_to: date | None = None,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Не задаём даты по умолчанию — сервис возьмёт диапазон по фактическим транзакциям
    service = ReportService(session)
    return await service.by_categories(user_id, date_from, date_to)


@router.get("/tax-estimate", response_model=TaxEstimateReport)
async def tax_estimate_report(
    date_from: date | None = None,
    date_to: date | None = None,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Не задаём даты по умолчанию — сервис возьмёт диапазон по фактическим транзакциям
    service = ReportService(session)
    return await service.tax_estimate(user_id, date_from, date_to)
