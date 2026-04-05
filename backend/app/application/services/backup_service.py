from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.infrastructure.db.models import (
    Account,
    BackupFile,
    CategorizationRule,
    Category,
    ForecastItem,
    ForecastSnapshot,
    ImportSession,
    MappingTemplate,
    Receivable,
    RecurringTransaction,
    RuleSuggestion,
    TaxProfile,
    Transaction,
)


def _parse_dt(val: Any) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    s = str(val).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime | date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(x) for x in obj]
    return obj


class BackupService:
    BACKUP_VERSION = 1

    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_snapshot(self, user_id: str) -> dict:
        categories = (
            await self.session.execute(select(Category).where(Category.user_id == user_id))
        ).scalars().all()
        accounts = (
            await self.session.execute(select(Account).where(Account.user_id == user_id))
        ).scalars().all()
        rules = (
            await self.session.execute(
                select(CategorizationRule).where(CategorizationRule.user_id == user_id)
            )
        ).scalars().all()
        txns = (
            await self.session.execute(select(Transaction).where(Transaction.user_id == user_id))
        ).scalars().all()
        recurring = (
            await self.session.execute(
                select(RecurringTransaction).where(RecurringTransaction.user_id == user_id)
            )
        ).scalars().all()
        receivables = (
            await self.session.execute(select(Receivable).where(Receivable.user_id == user_id))
        ).scalars().all()
        templates = (
            await self.session.execute(
                select(MappingTemplate).where(MappingTemplate.user_id == user_id)
            )
        ).scalars().all()
        suggestions = (
            await self.session.execute(select(RuleSuggestion).where(RuleSuggestion.user_id == user_id))
        ).scalars().all()
        tax_profiles = (
            await self.session.execute(select(TaxProfile).where(TaxProfile.user_id == user_id))
        ).scalars().all()
        imports = (
            await self.session.execute(select(ImportSession).where(ImportSession.user_id == user_id))
        ).scalars().all()
        snaps = (
            await self.session.execute(
                select(ForecastSnapshot).where(ForecastSnapshot.user_id == user_id)
            )
        ).scalars().all()
        snap_payload = []
        for s in snaps:
            items = (
                await self.session.execute(select(ForecastItem).where(ForecastItem.snapshot_id == s.id))
            ).scalars().all()
            snap_payload.append(
                {
                    "snapshot": {
                        "id": s.id,
                        "user_id": s.user_id,
                        "start_date": s.start_date,
                        "end_date": s.end_date,
                        "base_balance": s.base_balance,
                        "assumptions_json": s.assumptions_json,
                        "generated_at": s.generated_at,
                    },
                    "items": [
                        {
                            "id": i.id,
                            "snapshot_id": i.snapshot_id,
                            "forecast_date": i.forecast_date,
                            "opening_balance": i.opening_balance,
                            "inflow_amount": i.inflow_amount,
                            "outflow_amount": i.outflow_amount,
                            "closing_balance": i.closing_balance,
                            "explanation_json": i.explanation_json,
                        }
                        for i in items
                    ],
                }
            )

        def cat_row(c: Category) -> dict:
            return {
                "id": c.id,
                "user_id": c.user_id,
                "name": c.name,
                "type": c.type,
                "color": c.color,
                "is_system": c.is_system,
                "created_at": getattr(c, "created_at", None),
                "updated_at": getattr(c, "updated_at", None),
            }

        def acc_row(a: Account) -> dict:
            return {
                "id": a.id,
                "user_id": a.user_id,
                "name": a.name,
                "currency": a.currency,
                "source_type": getattr(a, "source_type", "csv"),
                "created_at": getattr(a, "created_at", None),
                "updated_at": getattr(a, "updated_at", None),
            }

        payload = {
            "version": self.BACKUP_VERSION,
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "categories": [cat_row(c) for c in categories],
            "accounts": [acc_row(a) for a in accounts],
            "categorization_rules": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "name": r.name,
                    "priority": r.priority,
                    "conditions_json": r.conditions_json,
                    "category_id": r.category_id,
                    "is_active": r.is_active,
                    "created_at": getattr(r, "created_at", None),
                    "updated_at": getattr(r, "updated_at", None),
                }
                for r in rules
            ],
            "transactions": [
                {
                    "id": t.id,
                    "user_id": t.user_id,
                    "account_id": t.account_id,
                    "external_hash": t.external_hash,
                    "operation_date": t.operation_date,
                    "amount": t.amount,
                    "currency": t.currency,
                    "direction": t.direction,
                    "description": t.description,
                    "counterparty": t.counterparty,
                    "normalized_description": t.normalized_description,
                    "category_id": t.category_id,
                    "transfer_group_id": t.transfer_group_id,
                    "is_manual": t.is_manual,
                    "is_duplicate": t.is_duplicate,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at,
                }
                for t in txns
            ],
            "recurring_transactions": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "name": r.name,
                    "amount": r.amount,
                    "currency": r.currency,
                    "direction": r.direction,
                    "category_id": r.category_id,
                    "recurrence_rule": r.recurrence_rule,
                    "next_run_date": r.next_run_date,
                    "source_hint": r.source_hint,
                    "is_confirmed": r.is_confirmed,
                    "is_active": r.is_active,
                    "created_at": getattr(r, "created_at", None),
                    "updated_at": getattr(r, "updated_at", None),
                }
                for r in recurring
            ],
            "receivables": [
                {
                    "id": x.id,
                    "user_id": x.user_id,
                    "title": x.title,
                    "expected_amount": x.expected_amount,
                    "currency": x.currency,
                    "expected_date": x.expected_date,
                    "counterparty": x.counterparty,
                    "status": x.status,
                    "linked_transaction_id": x.linked_transaction_id,
                    "created_at": getattr(x, "created_at", None),
                    "updated_at": getattr(x, "updated_at", None),
                }
                for x in receivables
            ],
            "mapping_templates": [
                {
                    "id": m.id,
                    "user_id": m.user_id,
                    "name": m.name,
                    "source_signature": m.source_signature,
                    "column_map": m.column_map,
                    "date_format": m.date_format,
                    "delimiter": m.delimiter,
                    "encoding": m.encoding,
                    "amount_sign_strategy": m.amount_sign_strategy,
                    "created_at": getattr(m, "created_at", None),
                    "updated_at": getattr(m, "updated_at", None),
                }
                for m in templates
            ],
            "rule_suggestions": [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "source_pattern": s.source_pattern,
                    "suggested_conditions_json": s.suggested_conditions_json,
                    "suggested_category_id": s.suggested_category_id,
                    "coverage_count": s.coverage_count,
                    "status": s.status,
                    "created_at": getattr(s, "created_at", None),
                    "updated_at": getattr(s, "updated_at", None),
                }
                for s in suggestions
            ],
            "tax_profiles": [
                {
                    "id": tp.id,
                    "user_id": tp.user_id,
                    "regime": tp.regime,
                    "rate_config_json": tp.rate_config_json,
                    "is_active": tp.is_active,
                    "created_at": getattr(tp, "created_at", None),
                    "updated_at": getattr(tp, "updated_at", None),
                }
                for tp in tax_profiles
            ],
            "import_sessions": [
                {
                    "id": imp.id,
                    "user_id": imp.user_id,
                    "source_filename": imp.source_filename,
                    "status": imp.status,
                    "detected_encoding": imp.detected_encoding,
                    "detected_delimiter": imp.detected_delimiter,
                    "mapping_template_id": imp.mapping_template_id,
                    "imported_rows": imp.imported_rows,
                    "skipped_rows": imp.skipped_rows,
                    "duplicate_rows": imp.duplicate_rows,
                    "started_at": imp.started_at,
                    "finished_at": imp.finished_at,
                }
                for imp in imports
            ],
            "forecast": snap_payload,
        }
        return _json_safe(payload)

    async def import_snapshot(self, user_id: str, data: dict, *, replace: bool) -> dict:
        if data.get("user_id") != user_id:
            raise ValidationError("user_id в архиве не совпадает с текущим пользователем", {})
        ver = data.get("version")
        if ver != self.BACKUP_VERSION:
            raise ValidationError("неподдерживаемая версия резервной копии", {"version": ver})

        if not replace:
            raise ValidationError(
                "импорт только с replace=true: полная замена данных пользователя",
                {},
            )

        await self._delete_user_data(user_id)
        # Фиксируем удаления до вставок — предотвращаем конфликты при смешанном flush.
        await self.session.flush()
        await self._insert_from_payload(user_id, data)
        return {"status": "imported", "replace": True}

    async def _delete_user_data(self, user_id: str) -> None:
        await self.session.execute(delete(Transaction).where(Transaction.user_id == user_id))
        await self.session.execute(
            delete(RecurringTransaction).where(RecurringTransaction.user_id == user_id)
        )
        await self.session.execute(delete(Receivable).where(Receivable.user_id == user_id))
        await self.session.execute(delete(RuleSuggestion).where(RuleSuggestion.user_id == user_id))
        await self.session.execute(
            delete(CategorizationRule).where(CategorizationRule.user_id == user_id)
        )

        snap_ids = (
            await self.session.execute(
                select(ForecastSnapshot.id).where(ForecastSnapshot.user_id == user_id)
            )
        ).scalars().all()
        for sid in snap_ids:
            await self.session.execute(delete(ForecastItem).where(ForecastItem.snapshot_id == sid))
        await self.session.execute(delete(ForecastSnapshot).where(ForecastSnapshot.user_id == user_id))

        await self.session.execute(delete(ImportSession).where(ImportSession.user_id == user_id))
        await self.session.execute(delete(MappingTemplate).where(MappingTemplate.user_id == user_id))
        await self.session.execute(delete(TaxProfile).where(TaxProfile.user_id == user_id))
        await self.session.execute(delete(BackupFile).where(BackupFile.user_id == user_id))
        await self.session.execute(delete(Category).where(Category.user_id == user_id))
        await self.session.execute(delete(Account).where(Account.user_id == user_id))

    async def _insert_from_payload(self, user_id: str, data: dict) -> None:
        # ── 1. Корневые таблицы без входящих FK ──────────────────────────────
        for row in data.get("categories") or []:
            self.session.add(
                Category(
                    id=row["id"],
                    user_id=user_id,
                    name=row["name"],
                    type=row["type"],
                    color=row.get("color"),
                    is_system=row.get("is_system", False),
                )
            )
        for row in data.get("accounts") or []:
            self.session.add(
                Account(
                    id=row["id"],
                    user_id=user_id,
                    name=row["name"],
                    currency=row.get("currency", "RUB"),
                    source_type=row.get("source_type", "csv"),
                )
            )
        for row in data.get("mapping_templates") or []:
            self.session.add(
                MappingTemplate(
                    id=row["id"],
                    user_id=user_id,
                    name=row["name"],
                    source_signature=row.get("source_signature"),
                    column_map=row["column_map"],
                    date_format=row.get("date_format", "%Y-%m-%d"),
                    delimiter=row.get("delimiter", ";"),
                    encoding=row.get("encoding", "utf-8"),
                    amount_sign_strategy=row.get("amount_sign_strategy", "column"),
                )
            )
        for row in data.get("tax_profiles") or []:
            self.session.add(
                TaxProfile(
                    id=row["id"],
                    user_id=user_id,
                    regime=row["regime"],
                    rate_config_json=row["rate_config_json"],
                    is_active=row.get("is_active", True),
                )
            )
        # Фиксируем родительские таблицы в БД до вставки дочерних.
        await self.session.flush()

        # ── 2. Таблицы, ссылающиеся на categories / accounts / mapping_templates
        for row in data.get("categorization_rules") or []:
            self.session.add(
                CategorizationRule(
                    id=row["id"],
                    user_id=user_id,
                    name=row["name"],
                    priority=row["priority"],
                    conditions_json=row["conditions_json"],
                    category_id=row["category_id"],
                    is_active=row.get("is_active", True),
                )
            )
        for row in data.get("transactions") or []:
            self.session.add(
                Transaction(
                    id=row["id"],
                    user_id=user_id,
                    account_id=row["account_id"],
                    external_hash=row["external_hash"],
                    operation_date=row["operation_date"]
                    if isinstance(row["operation_date"], date)
                    else date.fromisoformat(str(row["operation_date"])[:10]),
                    amount=Decimal(str(row["amount"])),
                    currency=row.get("currency", "RUB"),
                    direction=row["direction"],
                    description=row.get("description", ""),
                    counterparty=row.get("counterparty"),
                    normalized_description=row.get("normalized_description", ""),
                    category_id=row.get("category_id"),
                    transfer_group_id=row.get("transfer_group_id"),
                    is_manual=row.get("is_manual", False),
                    is_duplicate=row.get("is_duplicate", False),
                )
            )
        for row in data.get("recurring_transactions") or []:
            self.session.add(
                RecurringTransaction(
                    id=row["id"],
                    user_id=user_id,
                    name=row["name"],
                    amount=Decimal(str(row["amount"])),
                    currency=row.get("currency", "RUB"),
                    direction=row["direction"],
                    category_id=row.get("category_id"),
                    recurrence_rule=row["recurrence_rule"],
                    next_run_date=row["next_run_date"]
                    if isinstance(row["next_run_date"], date)
                    else date.fromisoformat(str(row["next_run_date"])[:10]),
                    source_hint=row.get("source_hint"),
                    is_confirmed=row.get("is_confirmed", False),
                    is_active=row.get("is_active", True),
                )
            )
        for row in data.get("rule_suggestions") or []:
            self.session.add(
                RuleSuggestion(
                    id=row["id"],
                    user_id=user_id,
                    source_pattern=row["source_pattern"],
                    suggested_conditions_json=row["suggested_conditions_json"],
                    suggested_category_id=row["suggested_category_id"],
                    coverage_count=row.get("coverage_count", 0),
                    status=row.get("status", "pending"),
                )
            )
        for row in data.get("import_sessions") or []:
            self.session.add(
                ImportSession(
                    id=row["id"],
                    user_id=user_id,
                    source_filename=row["source_filename"],
                    status=row.get("status", "completed"),
                    detected_encoding=row.get("detected_encoding"),
                    detected_delimiter=row.get("detected_delimiter"),
                    mapping_template_id=row.get("mapping_template_id"),
                    imported_rows=row.get("imported_rows", 0),
                    skipped_rows=row.get("skipped_rows", 0),
                    duplicate_rows=row.get("duplicate_rows", 0),
                    started_at=_parse_dt(row.get("started_at")) or datetime.now(timezone.utc),
                    finished_at=_parse_dt(row.get("finished_at")),
                )
            )
        await self.session.flush()

        # ── 3. Таблицы, ссылающиеся на transactions ───────────────────────────
        for row in data.get("receivables") or []:
            self.session.add(
                Receivable(
                    id=row["id"],
                    user_id=user_id,
                    title=row["title"],
                    expected_amount=Decimal(str(row["expected_amount"])),
                    currency=row.get("currency", "RUB"),
                    expected_date=row["expected_date"]
                    if isinstance(row["expected_date"], date)
                    else date.fromisoformat(str(row["expected_date"])[:10]),
                    counterparty=row.get("counterparty"),
                    status=row.get("status", "pending"),
                    linked_transaction_id=row.get("linked_transaction_id"),
                )
            )
        await self.session.flush()

        # ── 4. Прогноз (ForecastSnapshot → ForecastItem) ──────────────────────
        for block in data.get("forecast") or []:
            s = block["snapshot"]
            gen_at = _parse_dt(s.get("generated_at")) or datetime.now(timezone.utc)
            self.session.add(
                ForecastSnapshot(
                    id=s["id"],
                    user_id=user_id,
                    start_date=s["start_date"]
                    if isinstance(s["start_date"], date)
                    else date.fromisoformat(str(s["start_date"])[:10]),
                    end_date=s["end_date"]
                    if isinstance(s["end_date"], date)
                    else date.fromisoformat(str(s["end_date"])[:10]),
                    base_balance=Decimal(str(s["base_balance"])),
                    assumptions_json=s.get("assumptions_json") or {},
                    generated_at=gen_at,
                )
            )
        await self.session.flush()

        for block in data.get("forecast") or []:
            for i in block.get("items") or []:
                self.session.add(
                    ForecastItem(
                        id=i["id"],
                        snapshot_id=i["snapshot_id"],
                        forecast_date=i["forecast_date"]
                        if isinstance(i["forecast_date"], date)
                        else date.fromisoformat(str(i["forecast_date"])[:10]),
                        opening_balance=Decimal(str(i["opening_balance"])),
                        inflow_amount=Decimal(str(i.get("inflow_amount", 0))),
                        outflow_amount=Decimal(str(i.get("outflow_amount", 0))),
                        closing_balance=Decimal(str(i["closing_balance"])),
                        explanation_json=i.get("explanation_json") or {},
                    )
                )
        await self.session.flush()
