# Spec: Backup Management

## Backup File Model

```text
backup_files
  id           UUID PRIMARY KEY
  user_id      UUID NOT NULL → users.id
  filename     VARCHAR(255) NOT NULL
  created_at   TIMESTAMP DEFAULT NOW()
```

## Endpoints

### POST /backups/export
**Access:** Authenticated

**Response 200:**
```json
{
  "backup_id": "uuid",
  "filename": "fincontrol-backup-2026-03-11.json"
}
```

**Export contents may include:**
- user profile
- accounts
- categories
- rules
- transactions
- recurring payments
- receivables

---

### POST /backups/import
**Access:** Authenticated

**Request:** backup archive file

**Response 200:**
```json
{
  "restored": true,
  "entities": {
    "transactions": 120,
    "categories": 8,
    "rules": 6
  }
}
```

## Business Rules

1. User can export only own data.
2. Backup import must validate ownership and structure before restore.
3. Restore operation must not silently mix another user's data into current account.
4. Import/export actions should be auditable in logs.
