# Proposal: Receivables

## Summary

Implement receivables tracking so the user can record expected incoming payments and include them in balance forecast scenarios.

## Motivation

- Many self-employed users and microbusinesses depend on delayed customer payments.
- Forecast quality improves only when expected inflows are visible alongside recurring outflows.
- Users need a simple way to answer: who owes me money, how much, and when it matters.

## Scope

- Create receivable
- List receivables
- Filter by status and expected date
- Mark receivable as received or pending
- Include pending receivables in forecast

## Out of Scope

- Full invoicing workflow
- Payment provider integration
- Legal debt collection flows

## Design Overview

```text
User creates receivable
  → title, amount, expected date, counterparty
  → receivable remains pending
  → forecast includes pending receivable on expected date
```

Endpoints:
```text
GET    /receivables
POST   /receivables
PATCH  /receivables/:id
```

## Affected Components

- **Receivables** — primary component
- **Forecast** — consumes pending receivables
- **Reports** — may later include expected vs actual inflow views

## Decisions

1. **MVP state model** — `pending` and `received` are sufficient.
2. **Forecast input** — only pending receivables inside selected period affect forecast.
3. **Linking** — link to actual transaction is optional for MVP.

## Status

In Review
