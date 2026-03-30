from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base, TimestampMixin, gen_uuid


class RecurringTransaction(Base, TimestampMixin):
    __tablename__ = "recurring_transactions"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    direction: Mapped[str] = mapped_column(String(10))
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    recurrence_rule: Mapped[str] = mapped_column(String(100))
    next_run_date: Mapped[date] = mapped_column(Date, index=True)
    source_hint: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (Index("ix_recurring_user_next", "user_id", "next_run_date"),)
