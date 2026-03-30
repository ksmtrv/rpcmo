from datetime import date
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base, gen_uuid


class ForecastSnapshot(Base):
    __tablename__ = "forecast_snapshots"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    base_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    assumptions_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ForecastItem(Base):
    __tablename__ = "forecast_items"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("forecast_snapshots.id", ondelete="CASCADE"), index=True)
    forecast_date: Mapped[date] = mapped_column(Date)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    inflow_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    outflow_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    explanation_json: Mapped[dict] = mapped_column(JSONB, default=dict)
