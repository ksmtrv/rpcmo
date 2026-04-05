from pydantic import BaseModel, Field


class BackupExportEncryptedBody(BaseModel):
    passphrase: str = Field(..., min_length=8, max_length=512, description="Пароль для AES-GCM после PBKDF2")
