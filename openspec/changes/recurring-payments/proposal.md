# Proposal: Recurring Payments

## Summary

Implement recurring payment detection and management so the user can capture repeated obligations or repeated inflows and use them in forecast.

## Motivation

- Users often forget monthly outflows such as rent, internet, subscriptions, and services.
- Forecast quality depends on recurring payments being visible and explainable.
- Repeated transaction patterns can be partially detected automatically, then reviewed by the user.

## Scope

- List recurring transactions
- Detect recurring candidates from transaction history
- Store recurrence rule and next run date
- Confirm or keep candidate pending
- Include recurring items in forecast

## Out of Scope

- Full calendar engine with complex RRULE editor
- Automatic bank-side scheduling
- Advanced recurring anomaly detection

## Design Overview

```text
Transaction history
  → group similar transactions
  → estimate repeatability
  → create recurring candidate
  → user confirms / reviews
  → forecast includes next occurrences
```

Endpoints:
```text
GET  /recurring
POST /recurring/detect
```

## Affected Components

- **Recurring Payments** — primary component
- **Forecast** — consumes recurring occurrences
- **Transaction Management** — source history for detection

## Decisions

1. **MVP recurrence type** — monthly recurrence is sufficient.
2. **Candidate status** — item may remain unconfirmed and still be visible to user.
3. **Detection** — rule-based baseline may be extended with ML-assisted confidence.

## Status

In Review
