from pydantic import BaseModel


class CashflowReport(BaseModel):
    date_from: str
    date_to: str
    total_inflow: float
    total_outflow: float
    net: float
    by_date: list[dict]


class CategoriesReport(BaseModel):
    date_from: str
    date_to: str
    by_category: dict


class TaxEstimateReport(BaseModel):
    disclaimer: str
    date_from: str
    date_to: str
    income: float
    rate: float
    estimated_tax: float
