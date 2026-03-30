# Proposal: Transaction Management

## Summary

Implement transaction browsing, manual categorization, category management, categorization rules,
and rule suggestions that reduce repetitive user work after import.

## Motivation

- Imported data becomes useful only after it can be reviewed and categorized.
- Users need a clear place to fix mistakes, assign categories, and gradually automate recurring categorization work.
- Reports and forecasts depend on correctly categorized transactions.

## Scope

- Transaction list with filters and pagination
- Manual category assignment
- Bulk category assignment
- Category CRUD
- Categorization rule CRUD
- Suggested rule creation after repeated manual corrections
- Auto-categorization using rules and explainable heuristics/ML assistance

## Out of Scope

- Full accounting ledger
- Split transaction editor
- Approval workflows across multiple employees

## Design Overview

```text
Import → Transactions list
  → user fixes category manually
  → system proposes reusable rule
  → next imports auto-apply that rule
```

Core route groups:
```text
GET    /transactions
PATCH  /transactions/:id
POST   /transactions/bulk-categorize

GET    /categories
POST   /categories
PATCH  /categories/:id

GET    /rules
POST   /rules
PATCH  /rules/:id
DELETE /rules/:id
```

## Affected Components

- **Transaction Management** — primary component
- **Import Management** — feeds transactions
- **Reports** — reads categories and transaction flows
- **Forecast** — may use categorized outflows and obligations

## Decisions

1. **Categories** — user-scoped, editable.
2. **Rules** — ordered by priority, first matching rule wins.
3. **Manual override** — user can always replace auto-assigned category.
4. **Explainability** — auto-categorization must expose which rule or heuristic matched.

## Status

In Review
