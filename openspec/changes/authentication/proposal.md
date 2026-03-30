# Proposal: Authentication

## Summary

Implement user authentication for Fincontrol so that every financial workspace is tied to a specific user identity.
The user must log in before viewing imports, transactions, reports, forecasts, recurring payments, or backups.

## Motivation

- Financial data is personal and must not be exposed without authentication.
- The product already operates around user-scoped entities (`user_id`), so login must be explicit in the specification.
- Future sync, backups, and multi-device usage require a stable authenticated identity.

## Scope

- Login with email + password
- Registration for a new user
- Logout
- Current session endpoint (`/auth/me`)
- Protected access to all user financial data
- Per-user data isolation for accounts, imports, transactions, reports, recurring payments, receivables, and backups

## Out of Scope

- OAuth / social login
- Password reset by email
- Two-factor authentication
- Enterprise SSO

## Design Overview

```text
POST /auth/register   → create user account
POST /auth/login      → validate credentials, return token/session
POST /auth/logout     → terminate current session on client or server
GET  /auth/me         → return current authenticated user
```

All functional routes become protected:
- import
- transactions
- categories
- rules
- recurring
- receivables
- reports
- forecast
- backups

## Affected Components

- **Authentication** — primary component
- **Import Management** — imports belong to authenticated user
- **Transaction Management** — transactions must be scoped by authenticated user
- **Reports** — reports are built only from the current user's data
- **Recurring Payments** — detection and listing are user-specific
- **Forecast** — projections use only the current user's balances and obligations
- **Backup** — export/import is allowed only for authenticated user data

## Decisions

1. **Auth model** — email + password for MVP.
2. **Identity scope** — one authenticated user owns one logical financial workspace.
3. **Protected product** — no anonymous access to business data screens.
4. **Session transport** — implementation may use JWT or server-side session, but all protected routes must depend on authenticated identity.

## Status

In Review
