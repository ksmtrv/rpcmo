# Implementation Tasks: Transaction Management

## Tasks

### Backend
- [ ] Implement transaction list query with filters and pagination
- [ ] Implement single transaction category update
- [ ] Implement bulk categorization endpoint
- [ ] Implement category repository and CRUD endpoints
- [ ] Implement categorization rule repository and CRUD endpoints
- [ ] Add rule application service by priority
- [ ] Add suggested-rule generation after repeated manual fixes

### Frontend
- [ ] Transactions page with filters
- [ ] Category selector in transaction row
- [ ] Bulk categorize action
- [ ] Categories management page
- [ ] Rules management page

## Acceptance Criteria

- User can browse transactions by account and date range
- User can assign category manually for one or many transactions
- User can create and edit categories
- Active rules auto-apply in deterministic priority order
- User can always override auto-categorization manually
