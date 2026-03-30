# Spec: Transaction Management

## Transaction Model

```text
transactions
  id                     UUID PRIMARY KEY
  user_id                UUID NOT NULL → users.id
  account_id             UUID NOT NULL → accounts.id
  external_hash          VARCHAR(64) NOT NULL
  operation_date         DATE NOT NULL
  amount                 NUMERIC(15,2) NOT NULL
  currency               VARCHAR(3) NOT NULL
  direction              ENUM('in', 'out') NOT NULL
  description            VARCHAR(1024) NOT NULL
  counterparty           VARCHAR(255)
  normalized_description VARCHAR(1024) NOT NULL
  category_id            UUID NULL → categories.id
  is_manual              BOOLEAN DEFAULT FALSE
  is_duplicate           BOOLEAN DEFAULT FALSE
  created_at             TIMESTAMP DEFAULT NOW()
```

## Category Model

```text
categories
  id          UUID PRIMARY KEY
  user_id     UUID NOT NULL → users.id
  name        VARCHAR(255) NOT NULL
  type        ENUM('income', 'expense') NOT NULL
  color       VARCHAR(20)
  is_system   BOOLEAN DEFAULT FALSE
```

## Rule Model

```text
categorization_rules
  id              UUID PRIMARY KEY
  user_id         UUID NOT NULL → users.id
  name            VARCHAR(255) NOT NULL
  priority        INT NOT NULL DEFAULT 0
  conditions_json JSONB NOT NULL
  category_id     UUID NOT NULL → categories.id
  is_active       BOOLEAN DEFAULT TRUE
```

## Endpoints

### GET /transactions
**Access:** Authenticated

**Query params:** `account_id`, `date_from`, `date_to`, `page`, `size`

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "operation_date": "2025-01-16",
      "amount": -3500,
      "direction": "out",
      "description": "Оплата аренды",
      "category_id": "uuid|null"
    }
  ],
  "total": 120,
  "page": 1,
  "size": 50,
  "pages": 3
}
```

---

### PATCH /transactions/:id
**Access:** Authenticated

**Request:**
```json
{ "category_id": "uuid|null" }
```

**Response 200:** Updated transaction object

---

### POST /transactions/bulk-categorize
**Access:** Authenticated

**Request:**
```json
{
  "transaction_ids": ["uuid", "uuid"],
  "category_id": "uuid"
}
```

**Response 200:**
```json
{ "updated": 2 }
```

---

### GET /categories
**Access:** Authenticated

**Response 200:** List of user categories

---

### POST /categories
**Access:** Authenticated

**Request:**
```json
{
  "name": "Продукты и питание",
  "type": "expense",
  "color": "#22c55e"
}
```

**Response 201:** Created category

---

### PATCH /categories/:id
**Access:** Authenticated

**Request:** Partial update of name or color

---

### GET /rules
**Access:** Authenticated

**Response 200:**
```json
[
  {
    "id": "uuid",
    "name": "Интернет → Связь и интернет",
    "priority": 100,
    "category_id": "uuid"
  }
]
```

## Business Rules

1. User sees only own transactions, categories, and rules.
2. Category type must match transaction direction in auto-suggestions.
3. First active rule by priority wins.
4. Manual category change can be used to generate a suggested rule.
5. Auto-categorization must remain reversible by user.
