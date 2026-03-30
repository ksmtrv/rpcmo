from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.transactions import BulkCategorizeRequest, TransactionRead, TransactionUpdate
from app.application.services.categorization_service import CategorizationService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import TransactionRepository

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=dict)
async def list_transactions(
    account_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = TransactionRepository(session)
    offset = (page - 1) * size
    items, total = await repo.get_list(user_id, account_id, date_from, date_to, offset, size)
    pages = (total + size - 1) // size if total else 1
    return {
        "items": [TransactionRead.model_validate(t) for t in items],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.patch("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: str,
    body: TransactionUpdate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = TransactionRepository(session)
    txn = await repo.update_category(transaction_id, body.category_id)
    if not txn:
        from fastapi import HTTPException
        raise HTTPException(404, "Транзакция не найдена")
    return TransactionRead.model_validate(txn)


@router.post("/auto-categorize")
async def auto_categorize(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Авто-категоризация транзакций без категории по ключевым словам в назначении."""
    service = CategorizationService(session)
    return await service.auto_categorize_uncategorized(user_id)


@router.post("/bulk-categorize")
async def bulk_categorize(
    body: BulkCategorizeRequest,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = TransactionRepository(session)
    updated = 0
    for tid in body.transaction_ids:
        t = await repo.update_category(tid, body.category_id)
        if t:
            updated += 1
    return {"updated": updated}


@router.post("/manual")
async def create_manual(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from fastapi import HTTPException
    raise HTTPException(501, "Ручное создание транзакции — в разработке")
