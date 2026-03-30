from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.imports import ImportConfirmRequest, ImportConfirmResponse, ImportUploadResponse
from app.application.services.import_service import ImportService
from app.core.config import settings
from app.core.db import get_db
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/upload", response_model=ImportUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    content = await file.read()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    service = ImportService(session)
    result = await service.upload_and_preview(file.filename or "export.csv", content)
    import_id = result["import_id"]
    (Path(settings.upload_dir) / f"{import_id}.csv").write_bytes(content)
    return result


@router.post("/{import_id}/confirm", response_model=ImportConfirmResponse)
async def confirm_import(
    import_id: str,
    body: ImportConfirmRequest,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = ImportService(session)
    return await service.confirm_import(
        import_id,
        body.column_map,
        body.account_name,
        body.date_format,
    )


@router.get("/{import_id}")
async def get_import(
    import_id: str,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from app.infrastructure.db.repositories import ImportSessionRepository

    repo = ImportSessionRepository(session)
    sess = await repo.get_by_id(import_id)
    if not sess:
        return {"error": "not_found"}
    return {
        "id": sess.id,
        "status": sess.status,
        "imported_rows": sess.imported_rows,
        "skipped_rows": sess.skipped_rows,
        "duplicate_rows": sess.duplicate_rows,
    }


@router.get("/{import_id}/preview")
async def get_preview(
    import_id: str,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from app.infrastructure.csv.parser import parse_csv_rows

    path = Path(settings.upload_dir) / f"{import_id}.csv"
    if not path.exists():
        return {"error": "file_not_found"}
    content = path.read_bytes()
    headers, rows, enc, delim = parse_csv_rows(content)
    return {"headers": headers, "rows": rows[:20], "encoding": enc, "delimiter": delim}
