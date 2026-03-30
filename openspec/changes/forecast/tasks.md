# Implementation Tasks: Forecast

## Tasks

### Backend
- [ ] Implement current-balance calculation from transactions
- [ ] Implement `GET /forecast`
- [ ] Implement `POST /forecast/recalculate`
- [ ] Project recurring occurrences into requested date range
- [ ] Include pending receivables in daily forecast
- [ ] Add daily explanations to every forecast item
- [ ] Add optional ML / statistical trend signal with safe fallback

### Frontend
- [ ] Forecast chart page
- [ ] Daily breakdown list
- [ ] Warning display
- [ ] ML usage indicator when enabled

## Acceptance Criteria

- User sees a 14-day balance forecast by day
- Forecast includes recurring payments and pending receivables
- Daily breakdown matches chart values
- Forecast remains readable and explainable even when ML is enabled
