# Spec: Forecast

## Endpoints

### GET /forecast
**Access:** Authenticated

**Query params:** `days` (1..90, default 14)

**Response 200:**
```json
{
  "start_date": "2026-03-11",
  "end_date": "2026-03-25",
  "base_balance": 215350,
  "currency": "RUB",
  "items": [
    {
      "date": "2026-03-16",
      "opening_balance": 215350,
      "inflow_amount": 0,
      "outflow_amount": 3500,
      "closing_balance": 211850,
      "explanations": [
        {
          "type": "recurring",
          "title": "Оплата аренды",
          "amount": -3500
        }
      ]
    }
  ],
  "warnings": [],
  "ml_enabled": true
}
```

---

### POST /forecast/recalculate
**Access:** Authenticated

**Behavior:** recalculates same contract as `GET /forecast`

## Forecast Inputs

- Current user balance
- Recurring payment occurrences inside range
- Pending receivables inside range
- Historical trend or average daily spending drift

## Business Rules

1. Forecast is always daily.
2. Each day starts from previous day's closing balance.
3. Pending receivables increase inflow on their expected date.
4. Recurring outflows decrease balance on projected date.
5. Explainability is mandatory: factors must be listed in `explanations`.
6. If data is insufficient, service returns warning rather than silent failure.
7. ML may add signal, but final balance must remain consistent with visible daily factors.
