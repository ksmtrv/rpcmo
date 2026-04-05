from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.backups import BackupExportEncryptedBody
from app.application.services.backup_service import BackupService
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.domain.services.backup_crypto import encrypt_backup_payload, resolve_import_body

router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("/export")
async def export_backup(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = BackupService(session)
    payload = await service.export_snapshot(user_id)
    return JSONResponse(content=payload)


@router.post("/export")
async def export_backup_encrypted(
    body: BackupExportEncryptedBody,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Экспорт с шифрованием (PBKDF2 + AES-256-GCM). Пароль не сохраняется."""
    service = BackupService(session)
    plain = await service.export_snapshot(user_id)
    encrypted = encrypt_backup_payload(plain, body.passphrase)
    return JSONResponse(content=encrypted)


@router.post("/import")
async def import_backup(
    replace: bool = Query(False, description="Полная замена данных пользователя содержимым архива"),
    body: dict = Body(...),
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    snapshot = resolve_import_body(body)
    service = BackupService(session)
    return await service.import_snapshot(user_id, snapshot, replace=replace)
