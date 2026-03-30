# Spec: Authentication

## Actors

| Actor | Access |
|------|--------|
| User | Can register, log in, log out, and access only own financial data |
| System | Validates credentials, resolves identity, protects routes |

## Endpoints

### POST /auth/register
**Access:** Public

**Request:**
```json
{
  "email": "string, required, unique",
  "password": "string, required, min 8 chars",
  "full_name": "string, optional"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "string|null"
}
```

**Errors:**
- `400` — validation failed
- `409` — email already exists

---

### POST /auth/login
**Access:** Public

**Request:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response 200:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "string|null"
  },
  "token": "JWT or session token"
}
```

**Errors:**
- `401` — invalid credentials
- `403` — blocked or inactive account

---

### POST /auth/logout
**Access:** Authenticated

**Response 204:** No content

---

### GET /auth/me
**Access:** Authenticated

**Response 200:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "string|null",
  "status": "active"
}
```

## Authorization Rules

| Action | Access |
|--------|--------|
| Register | Public |
| Login | Public |
| Open dashboard | Authenticated |
| Import CSV | Authenticated |
| View transactions | Authenticated |
| Edit categories and rules | Authenticated |
| View reports | Authenticated |
| Detect recurring payments | Authenticated |
| Build forecast | Authenticated |
| Export / import backup | Authenticated |

## Route Protection

The following route groups MUST require authenticated identity:

- `/imports/*`
- `/transactions/*`
- `/categories/*`
- `/rules/*`
- `/recurring/*`
- `/receivables/*`
- `/reports/*`
- `/forecast/*`
- `/backups/*`

## User Model

```text
users
  id             UUID PRIMARY KEY
  email          VARCHAR(255) UNIQUE NOT NULL
  password_hash  VARCHAR(255) NOT NULL
  full_name      VARCHAR(255)
  status         ENUM('active', 'blocked') DEFAULT 'active'
  created_at     TIMESTAMP DEFAULT NOW()
  updated_at     TIMESTAMP DEFAULT NOW()
```

## Session Requirements

- Every protected request MUST resolve `current_user`
- Every user-owned entity MUST be filtered by authenticated `user_id`
- Anonymous access to financial screens is forbidden
- Session expiration behavior must be explicit in implementation docs
