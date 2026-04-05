from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class TransactionRead(BaseModel):
    id: str
    account_id: str
    operation_date: date
    amount: Decimal
    currency: str
    direction: str
    description: str
    counterparty: str | None
    category_id: str | None
    is_manual: bool
    is_duplicate: bool

    model_config = {"from_attributes": True}


class TransactionUpdate(BaseModel):
    category_id: str | None = None


class BulkCategorizeRequest(BaseModel):
    transaction_ids: list[str]
    category_id: str | None


class TransactionManualCreate(BaseModel):
    account_id: str
    operation_date: date
    amount: Decimal
    direction: str
    description: str = ""
    counterparty: str | None = None
    category_id: str | None = None
