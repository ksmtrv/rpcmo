# Spec: Recurring Payments

## Recurring Transaction Model

```text
recurring_transactions
  id               UUID PRIMARY KEY
  user_id          UUID NOT NULL → users.id
  name             VARCHAR(255) NOT NULL
  amount           NUMERIC(15,2) NOT NULL
  currency         VARCHAR(3) NOT NULL DEFAULT 'RUB'
  direction        ENUM('in', 'out') NOT NULL
  category_id      UUID NULL → categories.id
  recurrence_rule  VARCHAR(100) NOT NULL
  next_run_date    DATE NOT NULL
  source_hint      VARCHAR(512)
  is_confirmed     BOOLEAN DEFAULT FALSE
  is_active        BOOLEAN DEFAULT TRUE
```

## Endpoints

### GET /recurring
**Access:** Authenticated

**Response 200:**
```json
[
  {
    "id": "uuid",
    "name": "Оплата аренды",
    "amount": 3500,
    "currency": "RUB",
    "direction": "out",
    "category_id": "uuid|null",
    "recurrence_rule": "MONTHLY",
    "next_run_date": "2025-04-16",
    "is_confirmed": false,
    "is_active": true
  }
]
```

---

### POST /recurring/detect
**Access:** Authenticated

**Response 200:**
```json
{
  "detected": 4,
  "message": "Обнаружено регулярных платежей: 4"
}
```

## Detection Rules

1. Similar transactions may be grouped by normalized description, counterparty, and amount.
2. Monthly recurring pattern is acceptable when intervals are approximately monthly.
3. ML-assisted confidence may be used as an additional signal for borderline groups.
4. Existing active recurring item with same `source_hint` must not be duplicated.

## Forecast Integration

1. Recurring items generate occurrences inside forecast date range.
2. `MONTHLY` occurrence uses same day-of-month where possible.
3. User must see recurring explanation inside daily forecast breakdown.
