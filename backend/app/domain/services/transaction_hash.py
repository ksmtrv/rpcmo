import hashlib
from datetime import date
from decimal import Decimal


def compute_transaction_hash(
    operation_date: date,
    amount: Decimal,
    normalized_description: str,
    counterparty: str | None,
    account_id: str,
) -> str:
    parts = [
        str(operation_date),
        str(amount),
        (normalized_description or "").strip().lower(),
        (counterparty or "").strip().lower(),
        account_id,
    ]
    content = "|".join(parts)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
