from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Transaction
from app.infrastructure.db.repositories import RuleSuggestionRepository, TransactionRepository


class RuleSuggestionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.suggestion_repo = RuleSuggestionRepository(session)
        self.txn_repo = TransactionRepository(session)

    async def refresh_after_single_categorization(self, user_id: str, txn: Transaction) -> None:
        if not txn.category_id:
            return

        norm = (txn.normalized_description or "").strip()
        cp = (txn.counterparty or "").strip() or None

        if len(norm) < 3 and not cp:
            return

        coverage = await self.txn_repo.count_uncategorized_matching_pattern(user_id, norm, cp)
        if coverage < 1:
            return

        if len(norm) >= 3:
            conditions = {"normalized_description_equals": norm, "direction": txn.direction}
            source_pattern = norm[:512]
        else:
            conditions = {"counterparty_contains": cp, "direction": txn.direction}
            source_pattern = (cp or "")[:512]

        dup = await self.suggestion_repo.find_pending_duplicate(
            user_id, source_pattern, txn.category_id
        )
        if dup:
            dup.coverage_count = coverage
            dup.suggested_conditions_json = conditions
            await self.session.flush()
            return

        await self.suggestion_repo.create(
            user_id=user_id,
            source_pattern=source_pattern,
            suggested_conditions_json=conditions,
            suggested_category_id=txn.category_id,
            coverage_count=coverage,
        )
