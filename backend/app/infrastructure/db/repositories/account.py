from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Account


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, name: str, currency: str = "RUB") -> Account:
        acc = Account(user_id=user_id, name=name, currency=currency)
        self.session.add(acc)
        await self.session.flush()
        return acc

    async def get_by_user(self, user_id: str) -> list[Account]:
        result = await self.session.execute(select(Account).where(Account.user_id == user_id))
        return list(result.scalars().all())
