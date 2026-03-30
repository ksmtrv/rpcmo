from pydantic import BaseModel


class ImportUploadResponse(BaseModel):
    import_id: str
    headers: list[str]
    column_map: dict[str, str]
    encoding: str
    delimiter: str
    total_rows: int
    preview: list[dict]


class ImportConfirmRequest(BaseModel):
    column_map: dict[str, str]
    account_name: str = "Основной счёт"
    date_format: str = "%Y-%m-%d"


class ImportConfirmResponse(BaseModel):
    import_id: str
    status: str
    imported_rows: int
    skipped_rows: int
    duplicate_rows: int
