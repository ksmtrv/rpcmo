from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import ReceivableRepository

router = APIRouter(prefix="/receivables", tags=["receivables"])


@router.get("")
async def list_receivables(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = ReceivableRepository(session)
    items = await repo.get_by_user(user_id)
    return [
        {
            "id": r.id,
            "title": r.title,
            "expected_amount": float(r.expected_amount),
            "expected_date": str(r.expected_date),
            "status": r.status,
        }
        for r in items
    ]
