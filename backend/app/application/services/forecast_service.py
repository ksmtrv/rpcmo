from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Account, Receivable, RecurringTransaction, Transaction
from app.infrastructure.db.repositories import ForecastRepository, ReceivableRepository, RecurringRepository
from app.ml.balance_forecast import forecast_balance_ml


def _add_months(d: date, months: int) -> date:
    """Добавить месяцы к дате (учитывая конец месяца)."""
    year = d.year
    month = d.month
    month += months
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    day = min(d.day, 28)
    try:
        return date(year, month, min(d.day, (date(year, month + 1, 1) - timedelta(days=1)).day))
    except (ValueError, TypeError):
        return date(year, month, day)


def _recurring_occurrences_in_range(
    next_run: date, recurrence_rule: str, start: date, end: date
) -> list[date]:
    """Даты регулярного платежа в диапазоне [start, end]."""
    if recurrence_rule != "MONTHLY":
        return [next_run] if start <= next_run <= end else []
    occurrences = []
    d = next_run
    while d < start:
        d = _add_months(d, 1)
    while d <= end:
        occurrences.append(d)
        d = _add_months(d, 1)
    return occurrences


class ForecastService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.forecast_repo = ForecastRepository(session)
        self.recurring_repo = RecurringRepository(session)
        self.receivable_repo = ReceivableRepository(session)

    async def build_forecast(
        self,
        user_id: str,
        days: int = 14,
        base_balance: Decimal | None = None,
    ) -> dict:
        start = date.today()
        end = start + timedelta(days=days)

        if base_balance is None:
            base_balance = await self._get_current_balance(user_id)

        recurring = await self.recurring_repo.get_by_user(user_id)
        receivables = await self.receivable_repo.get_pending_by_date_range(user_id, start, end)

        # Средний дневной расход из истории (доставка, продукты, прочие мелкие траты)
        avg_daily_outflow = await self._get_avg_daily_outflow(user_id, recurring)

        # ML-прогноз баланса (если достаточно истории)
        ml_forecast_by_date: dict[date, float] = {}
        try:
            txn_result = await self.session.execute(
                select(Transaction.operation_date, Transaction.amount, Transaction.direction)
                .where(Transaction.user_id == user_id)
                .order_by(Transaction.operation_date)
            )
            txn_rows = txn_result.all()
            if txn_rows:
                dates = [r.operation_date for r in txn_rows]
                amounts = [float(r.amount) for r in txn_rows]
                directions = [r.direction for r in txn_rows]
                ml_results = forecast_balance_ml(
                    dates, amounts, directions, float(base_balance), days
                )
                ml_forecast_by_date = {d: bal for d, bal in ml_results}
        except Exception:
            ml_forecast_by_date = {}

        # Собираем все даты регулярных платежей в периоде (включая неподтверждённые)
        recurring_by_date: dict[date, list[RecurringTransaction]] = {}
        for r in recurring:
            for occ_date in _recurring_occurrences_in_range(
                r.next_run_date, r.recurrence_rule, start, end
            ):
                if occ_date not in recurring_by_date:
                    recurring_by_date[occ_date] = []
                recurring_by_date[occ_date].append(r)

        items = []
        warnings = []
        balance = base_balance
        use_ml = bool(ml_forecast_by_date)

        for i in range(days):
            d = start + timedelta(days=i)
            opening = balance
            inflow = Decimal("0")
            outflow = Decimal("0")
            explanations = []

            for r in recurring_by_date.get(d, []):
                amt = r.amount
                if r.direction == "out":
                    outflow += amt
                    explanations.append({
                        "type": "recurring",
                        "title": r.name + (" ✓" if r.is_confirmed else " (ожидает)"),
                        "amount": float(-amt),
                    })
                else:
                    inflow += amt
                    explanations.append({
                        "type": "recurring",
                        "title": r.name + (" ✓" if r.is_confirmed else " (ожидает)"),
                        "amount": float(amt),
                    })

            for rec in receivables:
                if rec.expected_date == d:
                    inflow += rec.expected_amount
                    explanations.append(
                        {"type": "receivable", "title": rec.title, "amount": float(rec.expected_amount)}
                    )

            # Средний дневной расход (продукты, доставка и т.п.)
            if avg_daily_outflow > 0:
                outflow += Decimal(str(avg_daily_outflow))
                explanations.append({
                    "type": "avg_daily",
                    "title": "Средний дневной расход (продукты, доставка и т.п.)",
                    "amount": -float(avg_daily_outflow),
                })

            balance = opening + inflow - outflow

            # ML: добавляем только дневное приращение (тренд), не заменяем баланс
            if use_ml and d in ml_forecast_by_date and i > 0:
                prev_d = start + timedelta(days=i - 1)
                if prev_d in ml_forecast_by_date:
                    ml_drift = ml_forecast_by_date[d] - ml_forecast_by_date[prev_d]
                    balance += Decimal(str(ml_drift))

            items.append(
                {
                    "date": d.isoformat(),
                    "opening_balance": float(opening),
                    "inflow_amount": float(inflow),
                    "outflow_amount": float(outflow),
                    "closing_balance": float(balance),
                    "explanations": explanations,
                }
            )

        if not receivables and not recurring_by_date:
            warnings.append("прогноз неполный: нет ожидаемых поступлений и регулярных платежей")

        return {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "base_balance": float(base_balance),
            "currency": "RUB",
            "items": items,
            "warnings": warnings,
            "ml_enabled": use_ml,
        }

    async def _get_avg_daily_outflow(
        self, user_id: str, recurring: list[RecurringTransaction]
    ) -> float:
        """
        Средний дневной расход из истории, исключая уже учтённые регулярные.
        Учитывает продукты, доставку, мелкие траты.
        """
        result = await self.session.execute(
            select(
                func.sum(case((Transaction.direction == "out", -Transaction.amount), else_=0)).label("total_out"),
                func.min(Transaction.operation_date).label("min_d"),
                func.max(Transaction.operation_date).label("max_d"),
            ).where(Transaction.user_id == user_id)
        )
        row = result.one()
        if not row or not row.min_d or not row.max_d or not row.total_out or row.total_out <= 0:
            return 0.0
        days_span = (row.max_d - row.min_d).days + 1
        if days_span < 7:
            return 0.0
        total_out = float(row.total_out)
        avg_total = total_out / days_span
        # Вычитаем долю регулярных (амортизированную по дням)
        recurring_monthly = sum(float(r.amount) for r in recurring if r.direction == "out")
        avg_recurring_per_day = recurring_monthly / 30.0
        avg_misc = max(0.0, avg_total - avg_recurring_per_day)
        return round(avg_misc, 2)

    async def _get_current_balance(self, user_id: str) -> Decimal:
        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(case((Transaction.direction == "in", Transaction.amount), else_=-Transaction.amount)),
                    0,
                )
            ).where(Transaction.user_id == user_id)
        )
        return Decimal(str(result.scalar() or 0))
