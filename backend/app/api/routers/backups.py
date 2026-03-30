from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/backups", tags=["backups"])


@router.post("/export")
async def export_backup(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return {"message": "Экспорт резервной копии — в разработке"}


@router.post("/import")
async def import_backup(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return {"message": "Импорт резервной копии — в разработке"}
