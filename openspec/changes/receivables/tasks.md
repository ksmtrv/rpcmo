# Implementation Tasks: Receivables

## Tasks

### Backend
- [ ] Create `receivables` table and repository
- [ ] Implement `GET /receivables`
- [ ] Implement `POST /receivables`
- [ ] Implement `PATCH /receivables/:id`
- [ ] Add forecast integration for pending receivables in date range

### Frontend
- [ ] Receivables list page
- [ ] New receivable form
- [ ] Status change action (`pending` / `received`)

## Acceptance Criteria

- User can create an expected incoming payment
- Pending receivables appear in forecast on expected date
- Received receivables stop affecting forecast
- User cannot access another user's receivables
