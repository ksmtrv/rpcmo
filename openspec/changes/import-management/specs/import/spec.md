# Spec: Import Management

## Import Session Model

```text
import_sessions
  id                  UUID PRIMARY KEY
  user_id             UUID NOT NULL → users.id
  source_filename     VARCHAR(255) NOT NULL
  status              ENUM('pending', 'completed', 'failed') NOT NULL
  detected_encoding   VARCHAR(50)
  detected_delimiter  VARCHAR(10)
  imported_rows       INT DEFAULT 0
  skipped_rows        INT DEFAULT 0
  duplicate_rows      INT DEFAULT 0
  mapping_template_id UUID NULL
  created_at          TIMESTAMP DEFAULT NOW()
```

## Endpoints

### POST /imports/upload
**Access:** Authenticated

**Request:** `multipart/form-data` with `file`

**Response 200:**
```json
{
  "import_id": "uuid",
  "headers": ["Дата", "Сумма", "Назначение"],
  "column_map": {
    "operation_date": "Дата",
    "amount": "Сумма",
    "description": "Назначение"
  },
  "encoding": "utf-8",
  "delimiter": ";",
  "total_rows": 120,
  "preview": [
    {
      "operation_date": "2025-01-15",
      "amount": "50000",
      "description": "Поступление от клиента"
    }
  ]
}
```

**Errors:**
- `400` — invalid file or unsupported structure
- `401` — unauthenticated

---

### POST /imports/:id/confirm
**Access:** Authenticated

**Request:**
```json
{
  "column_map": {
    "operation_date": "Дата",
    "amount": "Сумма",
    "description": "Назначение",
    "counterparty": "Контрагент",
    "direction": "Тип"
  },
  "account_name": "Основной счёт",
  "date_format": "%Y-%m-%d"
}
```

**Response 200:**
```json
{
  "import_id": "uuid",
  "status": "completed",
  "imported_rows": 110,
  "skipped_rows": 4,
  "duplicate_rows": 6
}
```

**Business rules:**
1. Rows with invalid date are skipped.
2. Missing required fields (`operation_date`, `amount`) fail confirmation.
3. Duplicate rows do not create transactions.
4. Amount sign is normalized by `direction`.

---

### GET /imports/:id
**Access:** Authenticated

**Response 200:**
```json
{
  "id": "uuid",
  "status": "completed",
  "imported_rows": 110,
  "skipped_rows": 4,
  "duplicate_rows": 6
}
```

---

### GET /imports/:id/preview
**Access:** Authenticated

**Response 200:**
```json
{
  "headers": ["Дата", "Сумма", "Назначение"],
  "rows": [{ "Дата": "2025-01-15", "Сумма": "50000" }],
  "encoding": "utf-8",
  "delimiter": ";"
}
```

## Mapping Template Model

```text
mapping_templates
  id            UUID PRIMARY KEY
  user_id       UUID NOT NULL → users.id
  name          VARCHAR(255) NOT NULL
  column_map    JSONB NOT NULL
  date_format   VARCHAR(50) NOT NULL
  delimiter     VARCHAR(10) NOT NULL
  encoding      VARCHAR(50) NOT NULL
  created_at    TIMESTAMP DEFAULT NOW()
```

## Acceptance Notes

- Import must be idempotent at row level via duplicate detection.
- Preview must not create transactions.
- Confirmation must create or reuse an account for the current user.
