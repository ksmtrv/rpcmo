from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import ImportSession


class ImportSessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs: object) -> ImportSession:
        sess = ImportSession(**kwargs)
        self.session.add(sess)
        await self.session.flush()
        return sess

    async def get_by_id(self, import_id: str) -> ImportSession | None:
        result = await self.session.execute(select(ImportSession).where(ImportSession.id == import_id))
        return result.scalar_one_or_none()

    async def update(self, sess: ImportSession, **kwargs: object) -> ImportSession:
        for k, v in kwargs.items():
            setattr(sess, k, v)
        await self.session.flush()
        return sess
