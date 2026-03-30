from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Transaction


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_transaction_date_range(self, user_id: str) -> tuple[date, date]:
        result = await self.session.execute(
            select(
                func.min(Transaction.operation_date).label("min_d"),
                func.max(Transaction.operation_date).label("max_d"),
            ).where(Transaction.user_id == user_id)
        )
        row = result.one()
        if row.min_d and row.max_d:
            return row.min_d, row.max_d
        today = date.today()
        return today - timedelta(days=30), today

    async def cashflow(
        self,
        user_id: str,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        if not date_from or not date_to:
            d_from, d_to = await self._get_transaction_date_range(user_id)
            date_from = date_from or d_from
            date_to = date_to or d_to

        totals = await self.session.execute(
            select(
                func.sum(case((Transaction.direction == "in", Transaction.amount), else_=0)).label("inflow"),
                func.sum(case((Transaction.direction == "out", Transaction.amount), else_=0)).label("outflow"),
            ).where(
                Transaction.user_id == user_id,
                Transaction.operation_date >= date_from,
                Transaction.operation_date <= date_to,
            )
        )
        t = totals.one()
        total_in = Decimal(str(t.inflow or 0))
        total_out = Decimal(str(t.outflow or 0))

        result = await self.session.execute(
            select(
                Transaction.operation_date,
                func.sum(case((Transaction.direction == "in", Transaction.amount), else_=-Transaction.amount)).label("net"),
            )
            .where(Transaction.user_id == user_id)
            .where(Transaction.operation_date >= date_from)
            .where(Transaction.operation_date <= date_to)
            .group_by(Transaction.operation_date)
            .order_by(Transaction.operation_date)
        )
        rows = result.all()

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_inflow": float(total_in),
            "total_outflow": float(total_out),
            "net": float(total_in - total_out),
            "by_date": [{"date": str(r.operation_date), "net": float(r.net or 0)} for r in rows],
        }

    async def by_categories(
        self,
        user_id: str,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        if not date_from or not date_to:
            d_from, d_to = await self._get_transaction_date_range(user_id)
            date_from = date_from or d_from
            date_to = date_to or d_to

        result = await self.session.execute(
            select(
                Transaction.category_id,
                Transaction.direction,
                func.sum(Transaction.amount).label("total"),
            )
            .where(Transaction.user_id == user_id)
            .where(Transaction.operation_date >= date_from)
            .where(Transaction.operation_date <= date_to)
            .group_by(Transaction.category_id, Transaction.direction)
        )
        by_cat: dict[str, dict[str, float]] = {}
        for r in result.all():
            cid = r.category_id or "uncategorized"
            if cid not in by_cat:
                by_cat[cid] = {"inflow": 0.0, "outflow": 0.0}
            if r.direction == "in":
                by_cat[cid]["inflow"] += float(r.total or 0)
            else:
                by_cat[cid]["outflow"] += float(r.total or 0)

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "by_category": by_cat,
        }

    async def tax_estimate(
        self,
        user_id: str,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        if not date_from or not date_to:
            d_from, d_to = await self._get_transaction_date_range(user_id)
            date_from = date_from or d_from
            date_to = date_to or d_to

        result = await self.session.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.user_id == user_id,
                Transaction.direction == "in",
                Transaction.operation_date >= date_from,
                Transaction.operation_date <= date_to,
            )
        )
        income = Decimal(str(result.scalar() or 0))
        rate = Decimal("0.06")
        tax = income * rate
        return {
            "disclaimer": "Оценка, не юридически точный расчёт",
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "income": float(income),
            "rate": float(rate),
            "estimated_tax": float(tax),
        }
