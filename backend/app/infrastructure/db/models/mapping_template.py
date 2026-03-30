from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, gen_uuid


class MappingTemplate(Base, TimestampMixin):
    __tablename__ = "mapping_templates"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    source_signature: Mapped[str | None] = mapped_column(String(64), nullable=True)
    column_map: Mapped[dict] = mapped_column(JSONB)
    date_format: Mapped[str] = mapped_column(String(50), default="%Y-%m-%d")
    delimiter: Mapped[str] = mapped_column(String(5), default=";")
    encoding: Mapped[str] = mapped_column(String(20), default="utf-8")
    amount_sign_strategy: Mapped[str] = mapped_column(String(50), default="column")
