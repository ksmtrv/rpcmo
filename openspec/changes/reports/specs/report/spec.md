# Spec: Reports

## Endpoints

### GET /reports/cashflow
**Access:** Authenticated

**Query params:** `date_from`, `date_to`

**Response 200:**
```json
{
  "date_from": "2025-01-15",
  "date_to": "2025-03-26",
  "total_inflow": 175000,
  "total_outflow": 40350,
  "net": 134650,
  "by_date": [
    { "date": "2025-01-15", "net": 50000 }
  ]
}
```

---

### GET /reports/categories
**Access:** Authenticated

**Query params:** `date_from`, `date_to`

**Response 200:**
```json
{
  "date_from": "2025-01-15",
  "date_to": "2025-03-26",
  "by_category": {
    "uncategorized": { "inflow": 0, "outflow": 1200 },
    "category-uuid": { "inflow": 0, "outflow": 3500 }
  }
}
```

---

### GET /reports/tax-estimate
**Access:** Authenticated

**Query params:** `date_from`, `date_to`

**Response 200:**
```json
{
  "disclaimer": "Оценка, не юридически точный расчёт",
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "income": 175000,
  "rate": 0.06,
  "estimated_tax": 10500
}
```

## Business Rules

1. Reports use only current user's transactions.
2. If period is omitted, service resolves actual min/max transaction dates for the user.
3. Tax estimate is based on inflow transactions only.
4. Uncategorized transactions remain visible and must not disappear from charts.
