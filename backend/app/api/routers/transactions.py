from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.transactions import (
    BulkCategorizeRequest,
    TransactionManualCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.application.services.categorization_service import CategorizationService
from app.application.services.rule_suggestion_service import RuleSuggestionService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.core.errors import ValidationError
from app.domain.services.text_normalize import normalize_description
from app.domain.services.transaction_hash import compute_transaction_hash
from app.infrastructure.db.repositories import AccountRepository, CategoryRepository, TransactionRepository

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
    txn = await repo.update_category(user_id, transaction_id, body.category_id)
    if not txn:
        from fastapi import HTTPException
        raise HTTPException(404, "Транзакция не найдена")
    if body.category_id is not None:
        sug = RuleSuggestionService(session)
        await sug.refresh_after_single_categorization(user_id, txn)
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
        t = await repo.update_category(user_id, tid, body.category_id)
        if t:
            updated += 1
    return {"updated": updated}


def _normalize_manual_amount(amount: Decimal, direction: str) -> Decimal:
    d = str(direction).lower()
    if d not in ("in", "out"):
        raise ValidationError("direction должен быть in или out", {})
    a = Decimal(str(amount))
    if d == "out" and a > 0:
        return -abs(a)
    if d == "in" and a < 0:
        return abs(a)
    return a


@router.post("/manual", response_model=TransactionRead)
async def create_manual(
    body: TransactionManualCreate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from fastapi import HTTPException

    acc_repo = AccountRepository(session)
    cat_repo = CategoryRepository(session)
    txn_repo = TransactionRepository(session)
    account = await acc_repo.get_by_id_for_user(user_id, body.account_id)
    if not account:
        raise HTTPException(404, "Счёт не найден")
    if body.category_id and not await cat_repo.get_by_id_for_user(user_id, body.category_id):
        raise HTTPException(400, "Категория не найдена")
    try:
        amt = _normalize_manual_amount(body.amount, body.direction)
    except ValidationError as e:
        raise HTTPException(400, e.message) from e
    desc = body.description or ""
    cp = body.counterparty
    norm_desc = normalize_description(desc)
    ext_hash = compute_transaction_hash(
        body.operation_date, amt, norm_desc, cp or None, account.id
    )
    if await txn_repo.get_by_hash(user_id, ext_hash):
        raise HTTPException(409, "Транзакция с такими полями уже существует")
    txn = await txn_repo.create(
        user_id=user_id,
        account_id=account.id,
        external_hash=ext_hash,
        operation_date=body.operation_date,
        amount=amt,
        currency=account.currency,
        direction=str(body.direction).lower(),
        description=desc,
        counterparty=cp,
        normalized_description=norm_desc,
        category_id=body.category_id,
        is_manual=True,
        is_duplicate=False,
    )
    return TransactionRead.model_validate(txn)
