from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, gen_uuid


class ImportSession(Base):
    __tablename__ = "import_sessions"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_filename: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    detected_encoding: Mapped[str | None] = mapped_column(String(20), nullable=True)
    detected_delimiter: Mapped[str | None] = mapped_column(String(5), nullable=True)
    mapping_template_id: Mapped[str | None] = mapped_column(ForeignKey("mapping_templates.id"), nullable=True)
    imported_rows: Mapped[int] = mapped_column(Integer, default=0)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_rows: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
