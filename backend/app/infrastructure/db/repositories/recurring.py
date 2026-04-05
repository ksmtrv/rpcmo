from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import RecurringTransaction


class RecurringRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id: str) -> list[RecurringTransaction]:
        result = await self.session.execute(
            select(RecurringTransaction)
            .where(RecurringTransaction.user_id == user_id)
            .where(RecurringTransaction.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_id_for_user(self, user_id: str, recurring_id: str) -> RecurringTransaction | None:
        result = await self.session.execute(
            select(RecurringTransaction).where(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.id == recurring_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_upcoming(self, user_id: str, end_date: date) -> list[RecurringTransaction]:
        result = await self.session.execute(
            select(RecurringTransaction)
            .where(RecurringTransaction.user_id == user_id)
            .where(RecurringTransaction.is_active == True)
            .where(RecurringTransaction.next_run_date <= end_date)
        )
        return list(result.scalars().all())
