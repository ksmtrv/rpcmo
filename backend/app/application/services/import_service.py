from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ValidationError
from app.domain.services.text_normalize import normalize_description
from app.domain.services.transaction_hash import compute_transaction_hash
from app.infrastructure.csv.parser import detect_delimiter, detect_encoding, map_row_to_transaction_data, parse_csv_rows
from app.application.services.auto_categorization import get_category_color, suggest_category
from app.application.services.rule_category_resolver import resolve_category_from_rules
from app.infrastructure.db.repositories import (
    AccountRepository,
    CategoryRepository,
    ImportSessionRepository,
    MappingTemplateRepository,
    TransactionRepository,
    UserRepository,
)


def parse_amount(amount_str: str, direction: str) -> Decimal:
    s = amount_str.replace(",", ".").replace(" ", "").strip()
    if not s:
        return Decimal("0")
    try:
        val = Decimal(s)
        if direction == "out" and val > 0:
            val = -val
        elif direction == "in" and val < 0:
            val = abs(val)
        return val
    except Exception:
        return Decimal("0")


def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> date | None:
    from datetime import datetime

    for f in [fmt, "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]:
        try:
            return datetime.strptime(date_str.strip(), f).date()
        except ValueError:
            continue
    return None


class ImportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.account_repo = AccountRepository(session)
        self.category_repo = CategoryRepository(session)
        self.import_repo = ImportSessionRepository(session)
        self.template_repo = MappingTemplateRepository(session)
        self.txn_repo = TransactionRepository(session)

    async def upload_and_preview(
        self,
        filename: str,
        content: bytes,
        column_map: dict[str, str] | None = None,
    ) -> dict:
        import_id = None
        for _ in range(1):
            user = await self.user_repo.get_or_create_local_user()
            enc = detect_encoding(content)
            delim = detect_delimiter(content.decode(enc, errors="replace").split("\n")[0][:200])

            headers, rows, _, _ = parse_csv_rows(content, enc, delim)
            required = {"operation_date", "amount"}
            if not column_map:
                column_map = self._guess_column_map(headers)
            mapped = set(column_map.values())
            missing = required - set(column_map.keys())
            if missing:
                raise ValidationError(
                    "не удалось сопоставить обязательные колонки",
                    {"missing_fields": list(missing)},
                )

            sess = await self.import_repo.create(
                user_id=user.id,
                source_filename=filename,
                status="pending",
                detected_encoding=enc,
                detected_delimiter=delim,
                imported_rows=0,
                skipped_rows=0,
                duplicate_rows=0,
            )
            import_id = sess.id

            preview_rows = []
            for i, row in enumerate(rows[:10]):
                data = map_row_to_transaction_data(row, column_map)
                preview_rows.append(data)

            return {
                "import_id": import_id,
                "headers": headers,
                "column_map": column_map,
                "encoding": enc,
                "delimiter": delim,
                "total_rows": len(rows),
                "preview": preview_rows,
            }
        return {}

    def _guess_column_map(self, headers: list[str]) -> dict[str, str]:
        guesses = {
            "operation_date": ["date", "дата", "операция", "дата операции"],
            "amount": ["amount", "сумма", "sum", "сумма операции"],
            "description": ["description", "описание", "назначение", "назначение платежа"],
            "counterparty": ["counterparty", "контрагент", "получатель", "отправитель"],
            "direction": ["direction", "тип", "приход", "расход"],
        }
        result = {}
        for target, candidates in guesses.items():
            for h in headers:
                if h and any(c in str(h).lower() for c in candidates):
                    result[target] = h
                    break
        return result

    async def confirm_import(
        self,
        import_id: str,
        column_map: dict[str, str],
        account_name: str = "Основной счёт",
        date_format: str = "%Y-%m-%d",
    ) -> dict:
        sess = await self.import_repo.get_by_id(import_id)
        if not sess:
            raise ValidationError("Импорт не найден")
        if sess.status == "completed":
            return {"import_id": import_id, "status": "completed", "duplicates_skipped": True}

        user = await self.user_repo.get_by_id(sess.user_id)
        if not user:
            raise ValidationError("Пользователь не найден")

        accounts = await self.account_repo.get_by_user(user.id)
        if not accounts:
            account = await self.account_repo.create(user.id, account_name)
        else:
            account = accounts[0]

        upload_path = Path(settings.upload_dir) / f"{import_id}.csv"
        if not upload_path.exists():
            raise ValidationError("Файл импорта не найден")

        content = upload_path.read_bytes()
        _, rows, enc, delim = parse_csv_rows(content, sess.detected_encoding, sess.detected_delimiter)

        imported = 0
        skipped = 0
        duplicates = 0

        for row in rows:
            data = map_row_to_transaction_data(row, column_map)
            op_date_str = data.get("operation_date") or data.get("date")
            amount_str = data.get("amount") or "0"
            desc = data.get("description") or ""
            counterparty = data.get("counterparty") or ""
            direction_raw = data.get("direction") or "out"

            op_date = parse_date(str(op_date_str), date_format)
            if not op_date:
                skipped += 1
                continue

            direction = "in" if str(direction_raw).lower() in ("in", "приход", "income", "1") else "out"
            amount = parse_amount(str(amount_str), direction)
            norm_desc = normalize_description(desc)

            category_id = await resolve_category_from_rules(
                self.session, user.id, desc, counterparty or None, direction
            )
            if not category_id:
                cat_name = suggest_category(desc, counterparty, direction)
                if cat_name:
                    cat_type = "expense" if direction == "out" else "income"
                    cat = await self.category_repo.get_or_create(
                        user.id, cat_name, cat_type, get_category_color(cat_name)
                    )
                    category_id = cat.id

            ext_hash = compute_transaction_hash(op_date, amount, norm_desc, counterparty or None, account.id)
            existing = await self.txn_repo.get_by_hash(user.id, ext_hash)
            if existing:
                duplicates += 1
                continue

            await self.txn_repo.create(
                user_id=user.id,
                account_id=account.id,
                external_hash=ext_hash,
                operation_date=op_date,
                amount=amount,
                currency=account.currency,
                direction=direction,
                description=desc,
                counterparty=counterparty or None,
                normalized_description=norm_desc,
                category_id=category_id,
                is_manual=False,
                is_duplicate=False,
            )
            imported += 1

        await self.import_repo.update(
            sess,
            status="completed",
            imported_rows=imported,
            skipped_rows=skipped,
            duplicate_rows=duplicates,
        )

        template = await self.template_repo.create(
            user_id=user.id,
            name=f"Шаблон: {sess.source_filename}",
            column_map=column_map,
            date_format=date_format,
            delimiter=delim,
            encoding=enc,
        )
        await self.import_repo.update(sess, mapping_template_id=template.id)

        return {
            "import_id": import_id,
            "status": "completed",
            "imported_rows": imported,
            "skipped_rows": skipped,
            "duplicate_rows": duplicates,
        }
