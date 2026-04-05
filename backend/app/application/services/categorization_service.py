"""Сервис авто-категоризации существующих транзакций."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auto_categorization import get_category_color, suggest_category
from app.application.services.rule_category_resolver import resolve_category_from_rules
from app.infrastructure.db.models import Transaction
from app.infrastructure.db.repositories import CategoryRepository, TransactionRepository


class CategorizationService:
    """Применяет авто-категоризацию к транзакциям без категории."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_repo = CategoryRepository(session)
        self.txn_repo = TransactionRepository(session)

    async def auto_categorize_uncategorized(self, user_id: str) -> dict:
        """Находит транзакции без категории и назначает по ключевым словам."""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.category_id.is_(None))
        )
        txns = list(result.scalars().all())
        updated = 0

        for t in txns:
            rid = await resolve_category_from_rules(
                self.session,
                user_id,
                t.description or "",
                t.counterparty,
                t.direction,
            )
            if rid:
                t.category_id = rid
                updated += 1
                continue

            cat_name = suggest_category(
                t.description or "",
                t.counterparty or "",
                t.direction,
            )
            if not cat_name:
                continue

            cat_type = "expense" if t.direction == "out" else "income"
            cat = await self.category_repo.get_or_create(
                user_id, cat_name, cat_type, get_category_color(cat_name)
            )
            t.category_id = cat.id
            updated += 1

        await self.session.flush()
        return {"updated": updated, "total_uncategorized": len(txns)}
