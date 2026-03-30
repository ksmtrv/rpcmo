from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import RecurringTransaction, Transaction

try:
    from app.ml.recurring_model import get_recurring_predictor
except ImportError:
    get_recurring_predictor = None


class RecurringDetectionService:
    """Детекция регулярных платежей по повторяющимся транзакциям."""

    MIN_OCCURRENCES = 2  # С ML можно выявлять с 2 транзакций
    MONTHLY_DAYS_MIN = 20
    MONTHLY_DAYS_MAX = 40
    ML_CONFIDENCE_THRESHOLD = 0.75

    def __init__(self, session: AsyncSession):
        self.session = session

    async def detect_and_create(self, user_id: str) -> dict:
        """Анализирует транзакции и создаёт записи регулярных платежей."""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.direction == "out")
            .order_by(Transaction.operation_date)
        )
        transactions = list(result.scalars().all())

        # Группируем по (описание+контрагент, сумма)
        groups: dict[tuple[str, Decimal], list[Transaction]] = defaultdict(list)
        for t in transactions:
            key = (self._group_key(t), abs(t.amount))
            groups[key].append(t)

        predictor = get_recurring_predictor() if get_recurring_predictor else None
        created = 0
        for (_, _), txns in groups.items():
            if len(txns) < self.MIN_OCCURRENCES:
                continue
            txns.sort(key=lambda t: t.operation_date)
            amounts = [float(abs(t.amount)) for t in txns]
            intervals = [
                (txns[i].operation_date - txns[i - 1].operation_date).days
                for i in range(1, len(txns))
            ]
            desc_len = len((txns[0].description or "") + (txns[0].counterparty or ""))
            has_cp = bool((txns[0].counterparty or "").strip())

            # Эвристика: строгий паттерн ИЛИ ML-предсказание с высокой уверенностью
            strict_ok = self._is_monthly_pattern(txns)
            ml_ok = False
            if predictor:
                try:
                    ml_proba = predictor.predict_proba(
                        len(txns), amounts, intervals, desc_len, has_cp
                    )
                    ml_ok = ml_proba >= self.ML_CONFIDENCE_THRESHOLD
                except Exception:
                    pass
            if not (strict_ok or ml_ok):
                continue

            name = self._display_name(txns[0])
            source_hint = self._source_hint(txns[0])
            existing = await self._get_by_source_hint(user_id, source_hint)
            if existing:
                continue

            last_date = txns[-1].operation_date
            avg_days = self._avg_interval_days(txns)
            next_run = last_date + timedelta(days=round(avg_days))

            rec = RecurringTransaction(
                user_id=user_id,
                name=name,
                amount=abs(txns[0].amount),
                currency=txns[0].currency or "RUB",
                direction="out",
                category_id=txns[0].category_id,
                recurrence_rule="MONTHLY",
                next_run_date=next_run,
                source_hint=source_hint,
                is_confirmed=False,
                is_active=True,
            )
            self.session.add(rec)
            created += 1

        await self.session.flush()
        return {"detected": created, "message": f"Обнаружено регулярных платежей: {created}"}

    def _group_key(self, t: Transaction) -> str:
        """Ключ для группировки: нормализованное описание + контрагент."""
        norm = (t.normalized_description or "").strip().lower()
        cp = (t.counterparty or "").strip().lower()
        if cp:
            return f"{norm}|{cp}" if norm else cp
        return norm or "unknown"

    def _display_name(self, t: Transaction) -> str:
        """Читаемое название для отображения."""
        desc = (t.description or "").strip()
        cp = (t.counterparty or "").strip()
        if desc and cp:
            return f"{desc} ({cp})"
        return desc or cp or "Регулярный платёж"

    def _source_hint(self, t: Transaction) -> str:
        key = self._group_key(t)
        return f"{key}|{abs(t.amount)}|out"

    def _is_monthly_pattern(self, txns: list[Transaction]) -> bool:
        """Строгий паттерн: все интервалы 20–40 дней."""
        if len(txns) < 2:
            return False
        for i in range(1, len(txns)):
            delta = (txns[i].operation_date - txns[i - 1].operation_date).days
            if delta < self.MONTHLY_DAYS_MIN or delta > self.MONTHLY_DAYS_MAX:
                return False
        return True

    def _avg_interval_days(self, txns: list[Transaction]) -> float:
        if len(txns) < 2:
            return 30.0
        total = 0
        for i in range(1, len(txns)):
            total += (txns[i].operation_date - txns[i - 1].operation_date).days
        return total / (len(txns) - 1)

    async def _get_by_source_hint(self, user_id: str, source_hint: str) -> RecurringTransaction | None:
        result = await self.session.execute(
            select(RecurringTransaction)
            .where(RecurringTransaction.user_id == user_id)
            .where(RecurringTransaction.source_hint == source_hint)
            .where(RecurringTransaction.is_active == True)
        )
        return result.scalar_one_or_none()
