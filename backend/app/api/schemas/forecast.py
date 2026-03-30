from pydantic import BaseModel


class ForecastItem(BaseModel):
    date: str
    opening_balance: float
    inflow_amount: float
    outflow_amount: float
    closing_balance: float
    explanations: list[dict]


class ForecastResponse(BaseModel):
    start_date: str
    end_date: str
    base_balance: float
    currency: str
    items: list[ForecastItem]
    warnings: list[str]
