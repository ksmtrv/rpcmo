# Proposal: Forecast

## Summary

Implement a 14-day explainable balance forecast that combines current balance, recurring payments,
expected receivables, and historical spending trend.

## Motivation

- The forecast is one of the main product promises.
- Users need to understand whether money will be enough in the next two weeks.
- A useful forecast must be transparent, daily, and based on visible factors rather than hidden logic.

## Scope

- Build 14-day daily forecast
- Start from current balance
- Add recurring payments by projected dates
- Add pending receivables by expected dates
- Support historical trend / ML-assisted signal
- Show explanation for each day

## Out of Scope

- Long-term annual budgeting
- Multi-scenario planning matrix
- Enterprise treasury planning

## Design Overview

```text
Current balance
  + expected receivables
  - recurring outflows
  - daily spending drift
  = projected closing balance per day
```

Endpoints:
```text
GET  /forecast?days=14
POST /forecast/recalculate?days=14
```

## Affected Components

- **Forecast** — primary component
- **Transactions** — source balance history
- **Recurring Payments** — projected obligations/inflows
- **Receivables** — expected incoming cash

## Decisions

1. **MVP horizon** — 14 days by default, configurable up to 90.
2. **Explainability** — every non-empty forecast day must list contributing factors.
3. **ML role** — optional additive signal; must not become a black box that hides business factors.

## Status

In Review
