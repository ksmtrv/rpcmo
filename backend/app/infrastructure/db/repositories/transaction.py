from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash(self, user_id: str, external_hash: str) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.user_id == user_id,
                Transaction.external_hash == external_hash,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs: object) -> Transaction:
        txn = Transaction(**kwargs)
        self.session.add(txn)
        await self.session.flush()
        return txn

    async def get_list(
        self,
        user_id: str,
        account_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Transaction], int]:
        base = select(Transaction).where(Transaction.user_id == user_id)
        count_base = select(func.count()).select_from(Transaction).where(Transaction.user_id == user_id)

        if account_id:
            base = base.where(Transaction.account_id == account_id)
            count_base = count_base.where(Transaction.account_id == account_id)
        if date_from:
            base = base.where(Transaction.operation_date >= date_from)
            count_base = count_base.where(Transaction.operation_date >= date_from)
        if date_to:
            base = base.where(Transaction.operation_date <= date_to)
            count_base = count_base.where(Transaction.operation_date <= date_to)

        total = (await self.session.execute(count_base)).scalar() or 0
        q = base.order_by(Transaction.operation_date.desc()).offset(offset).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all()), total

    async def get_by_id(self, user_id: str, transaction_id: str) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_category(
        self, user_id: str, transaction_id: str, category_id: str | None
    ) -> Transaction | None:
        txn = await self.get_by_id(user_id, transaction_id)
        if txn:
            txn.category_id = category_id
            await self.session.flush()
        return txn

    async def count_uncategorized_matching_pattern(
        self,
        user_id: str,
        normalized_description: str,
        counterparty: str | None,
    ) -> int:
        parts = []
        if normalized_description:
            parts.append(Transaction.normalized_description == normalized_description)
        if counterparty:
            parts.append(Transaction.counterparty == counterparty)
        if not parts:
            return 0
        q = (
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.category_id.is_(None))
            .where(or_(*parts))
        )
        result = await self.session.execute(q)
        return int(result.scalar() or 0)
