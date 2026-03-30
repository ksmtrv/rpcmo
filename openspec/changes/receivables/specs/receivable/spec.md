# Spec: Receivables

## Receivable Model

```text
receivables
  id                    UUID PRIMARY KEY
  user_id               UUID NOT NULL → users.id
  title                 VARCHAR(255) NOT NULL
  expected_amount       NUMERIC(15,2) NOT NULL
  currency              VARCHAR(3) NOT NULL DEFAULT 'RUB'
  expected_date         DATE NOT NULL
  counterparty          VARCHAR(255)
  status                ENUM('pending', 'received') NOT NULL DEFAULT 'pending'
  linked_transaction_id UUID NULL
  created_at            TIMESTAMP DEFAULT NOW()
```

## Endpoints

### GET /receivables
**Access:** Authenticated

**Query params:** `status`, `date_from`, `date_to`

**Response 200:**
```json
[
  {
    "id": "uuid",
    "title": "Оплата за проект",
    "expected_amount": 45000,
    "expected_date": "2025-02-10",
    "counterparty": "ООО Заказчик",
    "status": "pending"
  }
]
```

---

### POST /receivables
**Access:** Authenticated

**Request:**
```json
{
  "title": "Оплата за проект",
  "expected_amount": 45000,
  "expected_date": "2025-02-10",
  "counterparty": "ООО Заказчик"
}
```

**Response 201:** Created receivable

---

### PATCH /receivables/:id
**Access:** Authenticated

**Request:**
```json
{
  "status": "received"
}
```

**Response 200:** Updated receivable

## Business Rules

1. Only `pending` receivables affect forecast.
2. User can edit only own receivables.
3. `expected_amount` must be positive.
4. Status transition `pending -> received` is allowed; reverse transition is allowed only by explicit user action.
