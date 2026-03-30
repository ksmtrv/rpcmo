from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base, TimestampMixin, gen_uuid


class CategorizationRule(Base, TimestampMixin):
    __tablename__ = "categorization_rules"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    conditions_json: Mapped[dict] = mapped_column(JSONB)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (Index("ix_rules_user_active_priority", "user_id", "is_active", "priority"),)
