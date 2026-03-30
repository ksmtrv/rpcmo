from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import ForecastItem, ForecastSnapshot


class ForecastRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_snapshot(self, **kwargs: object) -> ForecastSnapshot:
        snap = ForecastSnapshot(**kwargs)
        self.session.add(snap)
        await self.session.flush()
        return snap

    async def add_item(self, **kwargs: object) -> ForecastItem:
        item = ForecastItem(**kwargs)
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_latest(self, user_id: str) -> ForecastSnapshot | None:
        result = await self.session.execute(
            select(ForecastSnapshot)
            .where(ForecastSnapshot.user_id == user_id)
            .order_by(ForecastSnapshot.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
