# Project: Fincontrol

## Overview

A local-first financial control system for self-employed professionals and microbusinesses.
The product helps users import bank statements, categorize transactions, track recurring payments,
estimate taxes, and understand projected cash balance.

**Source documents:**
- `Openspec ТЗ Финконтроль.md`

---

## Actors

| Actor | Description |
|-------|-------------|
| **User** | Self-employed person, freelancer, or microbusiness owner who imports statements, reviews reports, and manages forecasts. |
| **System** | Parses statements, detects duplicates, suggests categorization, calculates reports and forecasts. |

---

## Architecture

**Style:** local-first ready web application with layered backend and SPA frontend

```text
User / Browser
      ↕  HTTP/S
  Frontend SPA
      ↕
  Backend API
  ┌──────────────────────────┐
  │  Fincontrol Application  │
  │  ┌────────────────────┐  │
  │  │ API Layer          │  │
  │  ├────────────────────┤  │
  │  │ Application Layer  │  │
  │  ├────────────────────┤  │
  │  │ Domain Layer       │  │
  │  ├────────────────────┤  │
  │  │ Infrastructure     │  │
  │  └────────────────────┘  │
  └──────────────────────────┘
      ↕
  PostgreSQL / Redis / File Storage
```

---

## Components

| Component | Exposed Interface | Description |
|-----------|------------------|-------------|
| **Authentication** | Yes | Login, session identity, protected access to user data |
| **Import Management** | Yes | CSV import, column mapping, normalization, duplicate protection |
| **Transaction Management** | Yes | Transaction list, manual categorization, rule-based categorization |
| **Receivables** | Yes | Expected incoming payments and their effect on forecast |
| **Reports** | Yes | Cashflow, category breakdown, tax estimate |
| **Recurring Payments** | Yes | Detection and management of recurring transactions |
| **Forecast** | Yes | 14-day balance forecast with explanations |
| **Backup** | Yes | Export and restore user data |

---

## Key Flows

### User Flow
```text
Login
  ├── Import CSV statement
  │     → Detect encoding and delimiter
  │     → Map columns
  │     → Normalize transactions
  │     → Skip duplicates
  │
  ├── Review transactions
  │     → Categorize manually
  │     → Apply rules / suggestions
  │
  ├── View reports
  │     → Cashflow
  │     → Category breakdown
  │     → Tax estimate
  │
  └── Open forecast
        → Include recurring payments
        → Include expected inflows
        → Show projected balance by day
```

---

## Domain Model

| Entity | Key Fields |
|--------|-----------|
| `User` | id, email, passwordHash, fullName, status, createdAt |
| `Account` | id, userId, name, currency |
| `Transaction` | id, userId, accountId, operationDate, amount, direction, description, categoryId |
| `Category` | id, userId, name, type, color |
| `CategorizationRule` | id, userId, name, priority, conditions, categoryId |
| `RecurringTransaction` | id, userId, name, amount, recurrenceRule, nextRunDate, isConfirmed |
| `Receivable` | id, userId, title, expectedAmount, expectedDate, status |
| `ForecastSnapshot` | id, userId, startDate, endDate, baseBalance |
| `BackupFile` | id, userId, filename, createdAt |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite |
| Backend | Python 3.13, FastAPI |
| Database | PostgreSQL |
| Cache / Jobs | Redis, ARQ |
| Auth | Email + password login, session/JWT |

---

## Module Status

| Module | OpenSpec Proposal | Status |
|--------|------------------|--------|
| Authentication | `openspec/changes/authentication/` | Draft |
| Import Management | `openspec/changes/import-management/` | Draft |
| Transaction Management | `openspec/changes/transaction-management/` | Draft |
| Receivables | `openspec/changes/receivables/` | Draft |
| Reports | `openspec/changes/reports/` | Draft |
| Recurring Payments | `openspec/changes/recurring-payments/` | Draft |
| Forecast | `openspec/changes/forecast/` | Draft |
| Backup | `openspec/changes/backup-management/` | Draft |

---

## Conventions

- OpenSpec proposals live in `openspec/changes/<feature-slug>/`
- Authentication is required before access to user financial data
- Every user sees only their own accounts, transactions, reports, and backups
- All ML or heuristic suggestions must remain explainable and user-correctable
