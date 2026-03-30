from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class RecurringCreate(BaseModel):
    name: str
    amount: Decimal
    currency: str = "RUB"
    direction: str
    category_id: str | None = None
    recurrence_rule: str
    next_run_date: date


class RecurringRead(BaseModel):
    id: str
    name: str
    amount: Decimal
    currency: str
    direction: str
    category_id: str | None
    recurrence_rule: str
    next_run_date: date
    is_confirmed: bool
    is_active: bool

    model_config = {"from_attributes": True}
