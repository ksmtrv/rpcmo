from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Receivable


class ReceivableRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id: str) -> list[Receivable]:
        result = await self.session.execute(select(Receivable).where(Receivable.user_id == user_id))
        return list(result.scalars().all())

    async def get_pending_by_date_range(
        self, user_id: str, start_date: date, end_date: date
    ) -> list[Receivable]:
        result = await self.session.execute(
            select(Receivable)
            .where(Receivable.user_id == user_id)
            .where(Receivable.status == "pending")
            .where(Receivable.expected_date >= start_date)
            .where(Receivable.expected_date <= end_date)
        )
        return list(result.scalars().all())
