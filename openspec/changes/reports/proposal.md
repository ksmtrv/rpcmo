# Proposal: Reports

## Summary

Implement financial reports for cashflow, category breakdown, and tax estimate so the user can understand current financial picture immediately after import.

## Motivation

- Reports are the first visible payoff after import and categorization.
- Users need concise visibility into income, expenses, and category structure.
- Self-employed users also need a simple tax estimate, even if not legally exact.

## Scope

- Cashflow report
- Category report
- Tax estimate report
- Default report period based on actual transaction range
- Explicit response contracts for frontend charts

## Out of Scope

- Official бухгалтерский or legal tax report
- Multi-company consolidated analytics
- Advanced BI dashboard builder

## Design Overview

```text
GET /reports/cashflow
  → totals: inflow, outflow, net
  → by date series

GET /reports/categories
  → grouped inflow / outflow by category

GET /reports/tax-estimate
  → income × configured rate
```

## Affected Components

- **Reports** — primary component
- **Transaction Management** — source data
- **Categories** — category names used for grouping

## Decisions

1. **Default period** — actual transaction date range, not arbitrary last 30 days.
2. **Tax estimate** — informational only, not legally binding.
3. **Grouping** — uncategorized transactions must appear explicitly as `uncategorized`.

## Status

In Review
