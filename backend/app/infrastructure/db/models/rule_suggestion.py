from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base, TimestampMixin, gen_uuid


class RuleSuggestion(Base, TimestampMixin):
    __tablename__ = "rule_suggestions"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_pattern: Mapped[str] = mapped_column(String(512))
    suggested_conditions_json: Mapped[dict] = mapped_column(JSONB)
    suggested_category_id: Mapped[str] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    coverage_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
