from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, gen_uuid


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    external_hash: Mapped[str] = mapped_column(String(64), index=True)
    operation_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    direction: Mapped[str] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(String(1024), default="")
    counterparty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_description: Mapped[str] = mapped_column(String(1024), default="")
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    transfer_group_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_manual: Mapped[bool] = mapped_column(default=False)
    is_duplicate: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "operation_date"),
        Index("ix_transactions_user_hash", "user_id", "external_hash"),
        Index("ix_transactions_user_category", "user_id", "category_id"),
    )

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
