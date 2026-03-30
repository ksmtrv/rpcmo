# Proposal: Backup Management

## Summary

Implement export and restore of user financial data so the product remains trustworthy, portable, and local-first ready.

## Motivation

- Financial tools must give users control over their data.
- Backup is essential for trust and recovery.
- Local-first positioning requires explicit portability and restore path.

## Scope

- Export user data backup
- Import backup archive
- Store backup metadata
- Restrict backup operations to authenticated user

## Out of Scope

- Cloud sync across devices
- Automatic scheduled remote backups
- Encrypted key escrow service

## Design Overview

```text
POST /backups/export
  → gather user-owned entities
  → serialize archive
  → save metadata

POST /backups/import
  → validate archive
  → restore user-owned entities
```

## Affected Components

- **Backup** — primary component
- **Authentication** — restricts data export/import to current user
- **All user-owned modules** — data source for export

## Decisions

1. **Scope of export** — user-owned product data only.
2. **Restore mode** — explicit user-triggered import.
3. **Trust model** — backup is a product-level safety feature, not hidden infrastructure concern.

## Status

In Review
