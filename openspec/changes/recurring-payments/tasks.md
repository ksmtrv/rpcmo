# Implementation Tasks: Recurring Payments

## Tasks

### Backend
- [ ] Create `recurring_transactions` table and repository
- [ ] Implement `GET /recurring`
- [ ] Implement `POST /recurring/detect`
- [ ] Add grouping and repeatability detection logic
- [ ] Add duplicate protection by `source_hint`
- [ ] Project recurring occurrences into forecast range

### Frontend
- [ ] Recurring payments page
- [ ] "Detect" action
- [ ] Candidate list with next date and status

## Acceptance Criteria

- User can detect recurring candidates from imported history
- Same recurring source is not created twice
- Recurring items appear in forecast on projected dates
- User can distinguish confirmed and pending recurring items
