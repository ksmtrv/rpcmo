# Proposal: Import Management

## Summary

Implement CSV-based bank statement import for Fincontrol with a guided column-mapping flow,
normalization, duplicate protection, and preview before confirmation.

## Motivation

- Import is the primary entry point to the first useful result.
- Users need a predictable way to bring transaction history into the system in 3-5 minutes.
- Financial data imports must be explainable, retryable, and safe from accidental duplicates.

## Scope

- Upload CSV statement
- Detect delimiter and encoding
- Preview parsed rows
- Map source columns to target transaction fields
- Confirm import into normalized transactions
- Duplicate detection by stable transaction hash
- Import session status and counters
- Mapping template persistence for reuse

## Out of Scope

- Direct bank API integrations
- PDF / XLSX / OFX parsing
- Multi-file batch import wizard
- Automatic reconciliation with external providers

## Design Overview

```text
POST /imports/upload
  → store import session
  → parse CSV
  → detect encoding/delimiter
  → guess column map
  → return preview

POST /imports/:id/confirm
  → normalize rows
  → parse dates and amounts
  → compute duplicate hash
  → create transactions
  → save mapping template
```

## Affected Components

- **Import Management** — primary component
- **Transaction Management** — receives normalized transactions
- **Authentication** — import belongs to authenticated user

## Decisions

1. **Supported format for MVP** — CSV only.
2. **Import safety** — import is two-step: preview first, confirm second.
3. **Duplicate protection** — deterministic hash by date, amount, normalized description, counterparty, and account.
4. **User ownership** — imported data is always scoped to current authenticated user.

## Status

In Review
